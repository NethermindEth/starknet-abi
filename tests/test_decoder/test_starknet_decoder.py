from nethermind.starknet_abi import StarknetAbi
from tests.utils import load_abi


def test_decode_constructor_calldata():
    abi_json = load_abi("first_contract", 1)

    abi = StarknetAbi.from_json(abi_json)

    calldata = [
        0x067C2665FBDD32DED72C0665F9658C05A5F9233C8DE2002B3EBA8AE046174EFD,
        0x02221DEF5413ED3E128051D5DFF3EC816DBFB9DB4454B98F4AA47804CB7A13D2,
    ]

    decoded = abi.constructor.decode(calldata)

    assert decoded.inputs == {
        "address": "0x067c2665fbdd32ded72c0665f9658c05a5f9233c8de2002b3eba8ae046174efd",
        "value": "0x02221def5413ed3e128051d5dff3ec816dbfb9db4454b98f4aa47804cb7a13d2",
    }
