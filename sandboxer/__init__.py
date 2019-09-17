import ast
from . import runtime
import gevent

class Sandboxer(object):
    def __init__(self, code, filename, io):
        self.code = code
        self.filename = filename
        self.parsed = ast.parse(code, filename=filename)
        self.io = io


    def toSafe(self):
        self.handleNode(self.parsed, None, 0)
        ast.fix_missing_locations(self.parsed)

        def do():
            scope0 = runtime.Scope(io=self.io)
            scope0.filename = self.filename
            self.io["scope0"].append(scope0)
            runtime.fillScope0(scope0)

            exec(compile(self.parsed, filename=self.filename, mode="exec"), {"scope0": scope0})
            return scope0

        return do


    def handleNode(self, node, parent, scope):
        # Scope variables
        if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Param):
            return ast.Subscript(
                value=ast.Name(id="scope%s" % scope, ctx=ast.Load()),
                slice=ast.Index(value=ast.Str(s=node.id)),
                ctx=node.ctx
            )

        # Global
        if isinstance(node, ast.Global):
            res = []
            for name in node.names:
                res.append(ast.Expr(value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="scope%s" % scope, ctx=ast.Load()),
                        attr="inheritVariable",
                        ctx=ast.Load()
                    ),
                    args=[
                        ast.Name(id="scope0", ctx=ast.Load()),
                        ast.Str(s=name)
                    ],
                    keywords=[], starargs=None, kwargs=None
                )))
            return res

        # Import
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            none = ast.Name(id="None", ctx=ast.Load())

            names = ast.List(elts=[
                ast.Tuple(elts=[
                    ast.Str(s=name.name),
                    ast.Str(s=name.asname) if name.asname else none
                ], ctx=ast.Load())
                for name in node.names
            ], ctx=ast.Load())

            if isinstance(node, ast.ImportFrom):
                from_ = ast.Str(node.module) if node.module else none
                level = ast.Num(node.level or 0)
            else:
                from_ = none
                level = none

            return ast.Expr(value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="scope%s" % scope, ctx=ast.Load()),
                    attr="import_",
                    ctx=ast.Load()
                ),
                args=[names, from_, level],
                keywords=[], starargs=None, kwargs=None
            ))


        if isinstance(node, ast.FunctionDef):
            scope += 1

        if isinstance(node, ast.Lambda):
            # Handle arguments (default values) in parent scope
            args = self.handleNode(node.args, node, scope)
            if args is not None:
                node.args = args

            # Now increment scope and handle body
            scope += 1
            body = self.handleNode(node.body, node, scope)
            if body is not None:
                node.body = body
        else:
            for fieldname, value in ast.iter_fields(node):
                if isinstance(value, ast.AST):
                    res = self.handleNode(value, node, scope)
                    if res is not None:
                        setattr(node, fieldname, res)
                elif isinstance(value, list):
                    result = []
                    for child in value:
                        val = self.handleNode(child, node, scope)
                        if val is None:
                            result.append(child)
                        elif isinstance(val, list):
                            result += val
                        else:
                            result.append(val)
                    setattr(node, fieldname, result)

        # Add scope to functions
        if isinstance(node, ast.FunctionDef):
            node.body.insert(0, ast.Assign(
                targets=[ast.Name(id="scope%s" % scope, ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="scope%s" % (scope-1), ctx=ast.Load()),
                        attr="inherit",
                        ctx=ast.Load()
                    ),
                    args=[], keywords=[],
                    starargs=None, kwargs=None
                )
            ))

            # Arguments
            for arg in node.args.args:
                node.body.insert(1, ast.Assign(
                    targets=[ast.Subscript(
                        value=ast.Name(id="scope%s" % scope, ctx=ast.Load()),
                        slice=ast.Index(value=ast.Str(s=arg.arg)),
                        ctx=ast.Store()
                    )],
                    value=ast.Name(id=arg.arg, ctx=ast.Load())
                ))

            # Kw-only arguments
            for arg in node.args.kwonlyargs:
                node.body.insert(1, ast.Assign(
                    targets=[ast.Subscript(
                        value=ast.Name(id="scope%s" % scope, ctx=ast.Load()),
                        slice=ast.Index(value=ast.Str(s=arg.arg)),
                        ctx=ast.Store()
                    )],
                    value=ast.Name(id=arg.arg, ctx=ast.Load())
                ))

            # Vararg
            if node.args.vararg is not None:
                node.body.insert(1, ast.Assign(
                    targets=[ast.Subscript(
                        value=ast.Name(id="scope%s" % scope, ctx=ast.Load()),
                        slice=ast.Index(value=ast.Str(s=node.args.vararg.arg)),
                        ctx=ast.Store()
                    )],
                    value=ast.Name(id=node.args.vararg.arg, ctx=ast.Load())
                ))

            # Kwarg
            if node.args.kwarg is not None:
                node.body.insert(1, ast.Assign(
                    targets=[ast.Subscript(
                        value=ast.Name(id="scope%s" % scope, ctx=ast.Load()),
                        slice=ast.Index(value=ast.Str(s=node.args.kwarg.arg)),
                        ctx=ast.Store()
                    )],
                    value=ast.Name(id=node.args.kwarg.arg, ctx=ast.Load())
                ))

        # Save functions (not methods) to scope
        if isinstance(node, ast.FunctionDef) and not isinstance(parent, ast.ClassDef):
            oldname = node.name
            node.name = "_user_%s_%s_" % (oldname, scope)

            return [
                node,
                ast.Assign(
                    targets=[ast.Subscript(
                        value=ast.Name(id="scope%s" % (scope-1), ctx=ast.Load()),
                        slice=ast.Index(value=ast.Str(s=oldname)),
                        ctx=ast.Store()
                    )],
                    value=ast.Name(id=node.name, ctx=ast.Load())
                )
            ]

        # Save classes to scope
        if isinstance(node, ast.ClassDef) and not isinstance(parent, ast.ClassDef):
            oldname = node.name
            node.name = "_user_%s_%s_" % (oldname, scope)

            return [
                node,
                ast.Assign(
                    targets=[ast.Subscript(
                        value=ast.Name(id="scope%s" % scope, ctx=ast.Load()),
                        slice=ast.Index(value=ast.Str(s=oldname)),
                        ctx=ast.Store()
                    )],
                    value=ast.Name(id=node.name, ctx=ast.Load())
                )
            ]

        # Add scope to lambdas
        if isinstance(node, ast.Lambda):
            # lambda a: a
            # ->
            # lambda a: (lambda scope1: scope1["a"])(scope0.extend({"a": a}))

            # We save everything to dict, don't assign automatically
            dct = ast.Dict(keys=[], values=[])

            # Arguments
            for arg in node.args.args:
                dct.keys.append(ast.Str(s=arg.arg))
                dct.values.append(ast.Name(id=arg.arg, ctx=ast.Load()))

            # Vararg
            if node.args.vararg is not None:
                dct.keys.append(ast.Str(s=node.args.vararg))
                dct.values.append(ast.Name(id=node.args.vararg, ctx=ast.Load()))

            # Kwarg
            if node.args.kwarg is not None:
                dct.keys.append(ast.Str(s=node.args.kwarg))
                dct.values.append(ast.Name(id=node.args.kwarg, ctx=ast.Load()))

            node.body = ast.Call(
                func=ast.Lambda(
                    args=ast.arguments(
                        args=[
                            ast.arg(
                                arg="scope%s" % scope, annotation=None, ctx=ast.Load()
                            )
                        ],
                        kwonlyargs=[],
                        vararg=None, kwarg=None,
                        defaults=[], kw_defaults=[]
                    ),
                    body=node.body
                ),
                args=[
                    ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id="scope%s" % (scope - 1), ctx=ast.Load()),
                            attr="extend",
                            ctx=ast.Load()
                        ),
                        args=[dct], keywords=[],
                        starargs=None, kwargs=None
                    )
                ],
                keywords=[], starargs=None, kwargs=None
            )

        # Add except handler
        if isinstance(node, ast.ExceptHandler):
            if node.name is not None:
                node.name = "_exc"
                node.body.insert(0, ast.Assign(
                    targets=[ast.Subscript(
                        value=ast.Name(id="scope%s" % scope, ctx=ast.Load()),
                        slice=ast.Index(value=ast.Str(s=node.name)),
                        ctx=ast.Store()
                    )],
                    value=ast.Name(id="_exc", ctx=ast.Load())
                ))

        # Now do something to prevent object.__subclasses__() hacks and others
        if (
            isinstance(node, ast.Attribute) and
            ((
                node.attr.startswith("__") and
                node.attr.endswith("__")
            ) or (
                node.attr.startswith("func_")
            ))
        ):
            return ast.Subscript(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="scope0", ctx=ast.Load()),
                        attr="safeAttr",
                        ctx=ast.Load()
                    ),
                    args=[node.value],
                    keywords=[], starargs=None, kwargs=None
                ),
                slice=ast.Index(value=ast.Str(node.attr)),
                ctx=node.ctx
            )