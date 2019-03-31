import pathlib
import sys, os
from flashlexpi.sdk import FlashlexSDK

def main(argv):
    print("starting ledticker with flashlex.")
    fn = "{0}/flashlex-pi-python/keys/config.yml".format(pathlib.Path(__file__).resolve().parents[1])
    print(fn)
    sdk = FlashlexSDK(fn)
    print(sdk.getSubscribedMessages())


if __name__ == "__main__":
    main(sys.argv[1:])