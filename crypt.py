from Crypt import CryptBitcoin

allowed_names = (
	"newPrivatekey", "newSeed", "hdPrivatekey", "privatekeyToAddress", "sign",
	"verify"
)

def module(io):
	class Crypt:
		def __init__(self):
			for name in allowed_names:
				setattr(self, name, getattr(CryptBitcoin, name))

	return Crypt()