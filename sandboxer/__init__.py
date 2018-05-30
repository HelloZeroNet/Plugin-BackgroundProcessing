import ast
import random

class Sandboxer(object):
    def __init__(self, code, ext):
        self.code = code
        self.ext = ext
        self.parsed = ast.parse(code, filename="0background.%s" % ext)


    def toSafe(self):
        self.stuff_root = "_stuff_%s_" % (random.randint(0, 1000000))
        self.handleNode(self.parsed, None, 0)
        ast.fix_missing_locations(self.parsed)

        filename = "0background.%s" % self.ext
        def do():
            exec compile(self.parsed, filename=filename, mode="exec") in {}
        return do


    def handleNode(self, node, parent, scope):
        # Scope variables
        if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Param):
            return ast.Subscript(
                value=ast.Name(id="scope%s" % scope, ctx=node.ctx),
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
            names = ast.List(elts=[
                ast.Tuple(elts=[
                    ast.Str(s=name.name),
                    ast.Str(s=name.asname)
                ], ctx=ast.Load())
                for name in node.names
            ], ctx=ast.Load())

            none = ast.Name(id="None", ctx=ast.Load())
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
                        value=ast.Name(id="scope%s" % scope, ctx=arg.ctx),
                        slice=ast.Index(value=ast.Str(s=arg.id)),
                        ctx=arg.ctx
                    )],
                    value=ast.Name(id=arg.id, ctx=arg.ctx)
                ))

            # Vararg
            if node.args.vararg is not None:
                node.body.insert(1, ast.Assign(
                    targets=[ast.Subscript(
                        value=ast.Name(id="scope%s" % scope, ctx=arg.ctx),
                        slice=ast.Index(value=ast.Str(s=node.args.vararg)),
                        ctx=arg.ctx
                    )],
                    value=ast.Name(id=node.args.vararg, ctx=arg.ctx)
                ))

            # Kwarg
            if node.args.kwarg is not None:
                node.body.insert(1, ast.Assign(
                    targets=[ast.Subscript(
                        value=ast.Name(id="scope%s" % scope, ctx=arg.ctx),
                        slice=ast.Index(value=ast.Str(s=node.args.kwarg)),
                        ctx=arg.ctx
                    )],
                    value=ast.Name(id=node.args.kwarg, ctx=arg.ctx)
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