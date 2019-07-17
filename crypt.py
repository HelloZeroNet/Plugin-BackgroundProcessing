from Crypt import CryptBitcoin

try:
	from Crypt import Crypt
	CryptBitcoin.newSeed = Crypt.newSeed
except ImportError:
	Crypt = None


allowed_names = (
	"newPrivatekey", "newSeed", "hdPrivatekey", "privatekeyToAddress", "sign",
	"verify"
)

def module(io):
	class ExtendedCrypt:
		def __init__(self):
			for name in allowed_names:
				setattr(self, name, getattr(Crypt, name))

	class Crypt:
		def __init__(self):
			for name in allowed_names:
				setattr(self, name, getattr(CryptBitcoin, name))
			if Crypt is None:
				self.ex = None
			else:
				self.ex = ExtendedCrypt()

	return Crypt()