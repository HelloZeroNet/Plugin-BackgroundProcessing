from Crypt import CryptBitcoin

try:
	from Crypt import Cryptography
	CryptBitcoin.newSeed = Cryptography.newSeed
except ImportError:
	Cryptography = None


allowed_names = (
	"newPrivatekey", "newSeed", "hdPrivatekey", "privatekeyToAddress", "sign",
	"verify"
)

def module(io):
	class ExtendedCryptography:
		def __init__(self):
			for name in allowed_names:
				setattr(self, name, getattr(Cryptography, name))

	class Crypt:
		def __init__(self):
			for name in allowed_names:
				setattr(self, name, getattr(CryptBitcoin, name))
			if Cryptography is None:
				self.ex = None
			else:
				self.ex = ExtendedCryptography()

	return Crypt()