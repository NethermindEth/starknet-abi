contract_address = "0x49d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"
entry_point_selector = (
    "0x83afd3f4caedc6eebf44246fe54e38c95e3179a5ec9ea81740eca5b482d12e"
)
calldata = [
    "0x7916596feab669322f03b6df4e71f7b158e291fd8d273c0e53759d5b7240b4a",
    "0x116933ea5369f0",
    "0x0",
]
transfer_abi = {
    "type": "function",
    "name": "transfer",
    "inputs": [
        {
            "name": "recipient",
            "type": "core::starknet::contract_address::ContractAddress",
        },
        {"name": "amount", "type": "core::integer::u256"},
    ],
    "outputs": [{"type": "core::bool"}],
    "state_mutability": "external",
}

starknet_eth_abi = [
    {
        "type": "impl",
        "name": "MintableToken",
        "interface_name": "src::mintable_token_interface::IMintableToken",
    },
    {
        "type": "struct",
        "name": "core::integer::u256",
        "members": [
            {"name": "low", "type": "core::integer::u128"},
            {"name": "high", "type": "core::integer::u128"},
        ],
    },
    {
        "type": "interface",
        "name": "src::mintable_token_interface::IMintableToken",
        "items": [
            {
                "type": "function",
                "name": "permissioned_mint",
                "inputs": [
                    {
                        "name": "account",
                        "type": "core::starknet::contract_address::ContractAddress",
                    },
                    {"name": "amount", "type": "core::integer::u256"},
                ],
                "outputs": [],
                "state_mutability": "external",
            },
            {
                "type": "function",
                "name": "permissioned_burn",
                "inputs": [
                    {
                        "name": "account",
                        "type": "core::starknet::contract_address::ContractAddress",
                    },
                    {"name": "amount", "type": "core::integer::u256"},
                ],
                "outputs": [],
                "state_mutability": "external",
            },
        ],
    },
    {
        "type": "impl",
        "name": "MintableTokenCamelImpl",
        "interface_name": "src::mintable_token_interface::IMintableTokenCamel",
    },
    {
        "type": "interface",
        "name": "src::mintable_token_interface::IMintableTokenCamel",
        "items": [
            {
                "type": "function",
                "name": "permissionedMint",
                "inputs": [
                    {
                        "name": "account",
                        "type": "core::starknet::contract_address::ContractAddress",
                    },
                    {"name": "amount", "type": "core::integer::u256"},
                ],
                "outputs": [],
                "state_mutability": "external",
            },
            {
                "type": "function",
                "name": "permissionedBurn",
                "inputs": [
                    {
                        "name": "account",
                        "type": "core::starknet::contract_address::ContractAddress",
                    },
                    {"name": "amount", "type": "core::integer::u256"},
                ],
                "outputs": [],
                "state_mutability": "external",
            },
        ],
    },
    {
        "type": "impl",
        "name": "Replaceable",
        "interface_name": "src::replaceability_interface::IReplaceable",
    },
    {
        "type": "struct",
        "name": "core::array::Span::<core::felt252>",
        "members": [
            {"name": "snapshot", "type": "@core::array::Array::<core::felt252>"}
        ],
    },
    {
        "type": "struct",
        "name": "src::replaceability_interface::EICData",
        "members": [
            {"name": "eic_hash", "type": "core::starknet::class_hash::ClassHash"},
            {"name": "eic_init_data", "type": "core::array::Span::<core::felt252>"},
        ],
    },
    {
        "type": "enum",
        "name": "core::option::Option::<src::replaceability_interface::EICData>",
        "variants": [
            {"name": "Some", "type": "src::replaceability_interface::EICData"},
            {"name": "None", "type": "()"},
        ],
    },
    {
        "type": "enum",
        "name": "core::bool",
        "variants": [{"name": "False", "type": "()"}, {"name": "True", "type": "()"}],
    },
    {
        "type": "struct",
        "name": "src::replaceability_interface::ImplementationData",
        "members": [
            {"name": "impl_hash", "type": "core::starknet::class_hash::ClassHash"},
            {
                "name": "eic_data",
                "type": "core::option::Option::<src::replaceability_interface::EICData>",
            },
            {"name": "final", "type": "core::bool"},
        ],
    },
    {
        "type": "interface",
        "name": "src::replaceability_interface::IReplaceable",
        "items": [
            {
                "type": "function",
                "name": "get_upgrade_delay",
                "inputs": [],
                "outputs": [{"type": "core::integer::u64"}],
                "state_mutability": "view",
            },
            {
                "type": "function",
                "name": "get_impl_activation_time",
                "inputs": [
                    {
                        "name": "implementation_data",
                        "type": "src::replaceability_interface::ImplementationData",
                    }
                ],
                "outputs": [{"type": "core::integer::u64"}],
                "state_mutability": "view",
            },
            {
                "type": "function",
                "name": "add_new_implementation",
                "inputs": [
                    {
                        "name": "implementation_data",
                        "type": "src::replaceability_interface::ImplementationData",
                    }
                ],
                "outputs": [],
                "state_mutability": "external",
            },
            {
                "type": "function",
                "name": "remove_implementation",
                "inputs": [
                    {
                        "name": "implementation_data",
                        "type": "src::replaceability_interface::ImplementationData",
                    }
                ],
                "outputs": [],
                "state_mutability": "external",
            },
            {
                "type": "function",
                "name": "replace_to",
                "inputs": [
                    {
                        "name": "implementation_data",
                        "type": "src::replaceability_interface::ImplementationData",
                    }
                ],
                "outputs": [],
                "state_mutability": "external",
            },
        ],
    },
    {
        "type": "impl",
        "name": "AccessControlImplExternal",
        "interface_name": "src::access_control_interface::IAccessControl",
    },
    {
        "type": "interface",
        "name": "src::access_control_interface::IAccessControl",
        "items": [
            {
                "type": "function",
                "name": "has_role",
                "inputs": [
                    {"name": "role", "type": "core::felt252"},
                    {
                        "name": "account",
                        "type": "core::starknet::contract_address::ContractAddress",
                    },
                ],
                "outputs": [{"type": "core::bool"}],
                "state_mutability": "view",
            },
            {
                "type": "function",
                "name": "get_role_admin",
                "inputs": [{"name": "role", "type": "core::felt252"}],
                "outputs": [{"type": "core::felt252"}],
                "state_mutability": "view",
            },
        ],
    },
    {
        "type": "impl",
        "name": "RolesImpl",
        "interface_name": "src::roles_interface::IMinimalRoles",
    },
    {
        "type": "interface",
        "name": "src::roles_interface::IMinimalRoles",
        "items": [
            {
                "type": "function",
                "name": "is_governance_admin",
                "inputs": [
                    {
                        "name": "account",
                        "type": "core::starknet::contract_address::ContractAddress",
                    }
                ],
                "outputs": [{"type": "core::bool"}],
                "state_mutability": "view",
            },
            {
                "type": "function",
                "name": "is_upgrade_governor",
                "inputs": [
                    {
                        "name": "account",
                        "type": "core::starknet::contract_address::ContractAddress",
                    }
                ],
                "outputs": [{"type": "core::bool"}],
                "state_mutability": "view",
            },
            {
                "type": "function",
                "name": "register_governance_admin",
                "inputs": [
                    {
                        "name": "account",
                        "type": "core::starknet::contract_address::ContractAddress",
                    }
                ],
                "outputs": [],
                "state_mutability": "external",
            },
            {
                "type": "function",
                "name": "remove_governance_admin",
                "inputs": [
                    {
                        "name": "account",
                        "type": "core::starknet::contract_address::ContractAddress",
                    }
                ],
                "outputs": [],
                "state_mutability": "external",
            },
            {
                "type": "function",
                "name": "register_upgrade_governor",
                "inputs": [
                    {
                        "name": "account",
                        "type": "core::starknet::contract_address::ContractAddress",
                    }
                ],
                "outputs": [],
                "state_mutability": "external",
            },
            {
                "type": "function",
                "name": "remove_upgrade_governor",
                "inputs": [
                    {
                        "name": "account",
                        "type": "core::starknet::contract_address::ContractAddress",
                    }
                ],
                "outputs": [],
                "state_mutability": "external",
            },
            {
                "type": "function",
                "name": "renounce",
                "inputs": [{"name": "role", "type": "core::felt252"}],
                "outputs": [],
                "state_mutability": "external",
            },
        ],
    },
    {
        "type": "impl",
        "name": "ERC20Impl",
        "interface_name": "openzeppelin::token::erc20::interface::IERC20",
    },
    {
        "type": "interface",
        "name": "openzeppelin::token::erc20::interface::IERC20",
        "items": [
            {
                "type": "function",
                "name": "name",
                "inputs": [],
                "outputs": [{"type": "core::felt252"}],
                "state_mutability": "view",
            },
            {
                "type": "function",
                "name": "symbol",
                "inputs": [],
                "outputs": [{"type": "core::felt252"}],
                "state_mutability": "view",
            },
            {
                "type": "function",
                "name": "decimals",
                "inputs": [],
                "outputs": [{"type": "core::integer::u8"}],
                "state_mutability": "view",
            },
            {
                "type": "function",
                "name": "total_supply",
                "inputs": [],
                "outputs": [{"type": "core::integer::u256"}],
                "state_mutability": "view",
            },
            {
                "type": "function",
                "name": "balance_of",
                "inputs": [
                    {
                        "name": "account",
                        "type": "core::starknet::contract_address::ContractAddress",
                    }
                ],
                "outputs": [{"type": "core::integer::u256"}],
                "state_mutability": "view",
            },
            {
                "type": "function",
                "name": "allowance",
                "inputs": [
                    {
                        "name": "owner",
                        "type": "core::starknet::contract_address::ContractAddress",
                    },
                    {
                        "name": "spender",
                        "type": "core::starknet::contract_address::ContractAddress",
                    },
                ],
                "outputs": [{"type": "core::integer::u256"}],
                "state_mutability": "view",
            },
            {
                "type": "function",
                "name": "transfer",
                "inputs": [
                    {
                        "name": "recipient",
                        "type": "core::starknet::contract_address::ContractAddress",
                    },
                    {"name": "amount", "type": "core::integer::u256"},
                ],
                "outputs": [{"type": "core::bool"}],
                "state_mutability": "external",
            },
            {
                "type": "function",
                "name": "transfer_from",
                "inputs": [
                    {
                        "name": "sender",
                        "type": "core::starknet::contract_address::ContractAddress",
                    },
                    {
                        "name": "recipient",
                        "type": "core::starknet::contract_address::ContractAddress",
                    },
                    {"name": "amount", "type": "core::integer::u256"},
                ],
                "outputs": [{"type": "core::bool"}],
                "state_mutability": "external",
            },
            {
                "type": "function",
                "name": "approve",
                "inputs": [
                    {
                        "name": "spender",
                        "type": "core::starknet::contract_address::ContractAddress",
                    },
                    {"name": "amount", "type": "core::integer::u256"},
                ],
                "outputs": [{"type": "core::bool"}],
                "state_mutability": "external",
            },
        ],
    },
    {
        "type": "impl",
        "name": "ERC20CamelOnlyImpl",
        "interface_name": "openzeppelin::token::erc20::interface::IERC20CamelOnly",
    },
    {
        "type": "interface",
        "name": "openzeppelin::token::erc20::interface::IERC20CamelOnly",
        "items": [
            {
                "type": "function",
                "name": "totalSupply",
                "inputs": [],
                "outputs": [{"type": "core::integer::u256"}],
                "state_mutability": "view",
            },
            {
                "type": "function",
                "name": "balanceOf",
                "inputs": [
                    {
                        "name": "account",
                        "type": "core::starknet::contract_address::ContractAddress",
                    }
                ],
                "outputs": [{"type": "core::integer::u256"}],
                "state_mutability": "view",
            },
            {
                "type": "function",
                "name": "transferFrom",
                "inputs": [
                    {
                        "name": "sender",
                        "type": "core::starknet::contract_address::ContractAddress",
                    },
                    {
                        "name": "recipient",
                        "type": "core::starknet::contract_address::ContractAddress",
                    },
                    {"name": "amount", "type": "core::integer::u256"},
                ],
                "outputs": [{"type": "core::bool"}],
                "state_mutability": "external",
            },
        ],
    },
    {
        "type": "constructor",
        "name": "constructor",
        "inputs": [
            {"name": "name", "type": "core::felt252"},
            {"name": "symbol", "type": "core::felt252"},
            {"name": "decimals", "type": "core::integer::u8"},
            {"name": "initial_supply", "type": "core::integer::u256"},
            {
                "name": "recipient",
                "type": "core::starknet::contract_address::ContractAddress",
            },
            {
                "name": "permitted_minter",
                "type": "core::starknet::contract_address::ContractAddress",
            },
            {
                "name": "provisional_governance_admin",
                "type": "core::starknet::contract_address::ContractAddress",
            },
            {"name": "upgrade_delay", "type": "core::integer::u64"},
        ],
    },
    {
        "type": "function",
        "name": "increase_allowance",
        "inputs": [
            {
                "name": "spender",
                "type": "core::starknet::contract_address::ContractAddress",
            },
            {"name": "added_value", "type": "core::integer::u256"},
        ],
        "outputs": [{"type": "core::bool"}],
        "state_mutability": "external",
    },
    {
        "type": "function",
        "name": "decrease_allowance",
        "inputs": [
            {
                "name": "spender",
                "type": "core::starknet::contract_address::ContractAddress",
            },
            {"name": "subtracted_value", "type": "core::integer::u256"},
        ],
        "outputs": [{"type": "core::bool"}],
        "state_mutability": "external",
    },
    {
        "type": "function",
        "name": "increaseAllowance",
        "inputs": [
            {
                "name": "spender",
                "type": "core::starknet::contract_address::ContractAddress",
            },
            {"name": "addedValue", "type": "core::integer::u256"},
        ],
        "outputs": [{"type": "core::bool"}],
        "state_mutability": "external",
    },
    {
        "type": "function",
        "name": "decreaseAllowance",
        "inputs": [
            {
                "name": "spender",
                "type": "core::starknet::contract_address::ContractAddress",
            },
            {"name": "subtractedValue", "type": "core::integer::u256"},
        ],
        "outputs": [{"type": "core::bool"}],
        "state_mutability": "external",
    },
    {
        "type": "event",
        "name": "openzeppelin::token::erc20_v070::erc20::ERC20::Transfer",
        "kind": "struct",
        "members": [
            {
                "name": "from",
                "type": "core::starknet::contract_address::ContractAddress",
                "kind": "data",
            },
            {
                "name": "to",
                "type": "core::starknet::contract_address::ContractAddress",
                "kind": "data",
            },
            {"name": "value", "type": "core::integer::u256", "kind": "data"},
        ],
    },
    {
        "type": "event",
        "name": "openzeppelin::token::erc20_v070::erc20::ERC20::Approval",
        "kind": "struct",
        "members": [
            {
                "name": "owner",
                "type": "core::starknet::contract_address::ContractAddress",
                "kind": "data",
            },
            {
                "name": "spender",
                "type": "core::starknet::contract_address::ContractAddress",
                "kind": "data",
            },
            {"name": "value", "type": "core::integer::u256", "kind": "data"},
        ],
    },
    {
        "type": "event",
        "name": "src::replaceability_interface::ImplementationAdded",
        "kind": "struct",
        "members": [
            {
                "name": "implementation_data",
                "type": "src::replaceability_interface::ImplementationData",
                "kind": "data",
            }
        ],
    },
    {
        "type": "event",
        "name": "src::replaceability_interface::ImplementationRemoved",
        "kind": "struct",
        "members": [
            {
                "name": "implementation_data",
                "type": "src::replaceability_interface::ImplementationData",
                "kind": "data",
            }
        ],
    },
    {
        "type": "event",
        "name": "src::replaceability_interface::ImplementationReplaced",
        "kind": "struct",
        "members": [
            {
                "name": "implementation_data",
                "type": "src::replaceability_interface::ImplementationData",
                "kind": "data",
            }
        ],
    },
    {
        "type": "event",
        "name": "src::replaceability_interface::ImplementationFinalized",
        "kind": "struct",
        "members": [
            {
                "name": "impl_hash",
                "type": "core::starknet::class_hash::ClassHash",
                "kind": "data",
            }
        ],
    },
    {
        "type": "event",
        "name": "src::access_control_interface::RoleGranted",
        "kind": "struct",
        "members": [
            {"name": "role", "type": "core::felt252", "kind": "data"},
            {
                "name": "account",
                "type": "core::starknet::contract_address::ContractAddress",
                "kind": "data",
            },
            {
                "name": "sender",
                "type": "core::starknet::contract_address::ContractAddress",
                "kind": "data",
            },
        ],
    },
    {
        "type": "event",
        "name": "src::access_control_interface::RoleRevoked",
        "kind": "struct",
        "members": [
            {"name": "role", "type": "core::felt252", "kind": "data"},
            {
                "name": "account",
                "type": "core::starknet::contract_address::ContractAddress",
                "kind": "data",
            },
            {
                "name": "sender",
                "type": "core::starknet::contract_address::ContractAddress",
                "kind": "data",
            },
        ],
    },
    {
        "type": "event",
        "name": "src::access_control_interface::RoleAdminChanged",
        "kind": "struct",
        "members": [
            {"name": "role", "type": "core::felt252", "kind": "data"},
            {"name": "previous_admin_role", "type": "core::felt252", "kind": "data"},
            {"name": "new_admin_role", "type": "core::felt252", "kind": "data"},
        ],
    },
    {
        "type": "event",
        "name": "src::roles_interface::GovernanceAdminAdded",
        "kind": "struct",
        "members": [
            {
                "name": "added_account",
                "type": "core::starknet::contract_address::ContractAddress",
                "kind": "data",
            },
            {
                "name": "added_by",
                "type": "core::starknet::contract_address::ContractAddress",
                "kind": "data",
            },
        ],
    },
    {
        "type": "event",
        "name": "src::roles_interface::GovernanceAdminRemoved",
        "kind": "struct",
        "members": [
            {
                "name": "removed_account",
                "type": "core::starknet::contract_address::ContractAddress",
                "kind": "data",
            },
            {
                "name": "removed_by",
                "type": "core::starknet::contract_address::ContractAddress",
                "kind": "data",
            },
        ],
    },
    {
        "type": "event",
        "name": "src::roles_interface::UpgradeGovernorAdded",
        "kind": "struct",
        "members": [
            {
                "name": "added_account",
                "type": "core::starknet::contract_address::ContractAddress",
                "kind": "data",
            },
            {
                "name": "added_by",
                "type": "core::starknet::contract_address::ContractAddress",
                "kind": "data",
            },
        ],
    },
    {
        "type": "event",
        "name": "src::roles_interface::UpgradeGovernorRemoved",
        "kind": "struct",
        "members": [
            {
                "name": "removed_account",
                "type": "core::starknet::contract_address::ContractAddress",
                "kind": "data",
            },
            {
                "name": "removed_by",
                "type": "core::starknet::contract_address::ContractAddress",
                "kind": "data",
            },
        ],
    },
    {
        "type": "event",
        "name": "openzeppelin::token::erc20_v070::erc20::ERC20::Event",
        "kind": "enum",
        "variants": [
            {
                "name": "Transfer",
                "type": "openzeppelin::token::erc20_v070::erc20::ERC20::Transfer",
                "kind": "nested",
            },
            {
                "name": "Approval",
                "type": "openzeppelin::token::erc20_v070::erc20::ERC20::Approval",
                "kind": "nested",
            },
            {
                "name": "ImplementationAdded",
                "type": "src::replaceability_interface::ImplementationAdded",
                "kind": "nested",
            },
            {
                "name": "ImplementationRemoved",
                "type": "src::replaceability_interface::ImplementationRemoved",
                "kind": "nested",
            },
            {
                "name": "ImplementationReplaced",
                "type": "src::replaceability_interface::ImplementationReplaced",
                "kind": "nested",
            },
            {
                "name": "ImplementationFinalized",
                "type": "src::replaceability_interface::ImplementationFinalized",
                "kind": "nested",
            },
            {
                "name": "RoleGranted",
                "type": "src::access_control_interface::RoleGranted",
                "kind": "nested",
            },
            {
                "name": "RoleRevoked",
                "type": "src::access_control_interface::RoleRevoked",
                "kind": "nested",
            },
            {
                "name": "RoleAdminChanged",
                "type": "src::access_control_interface::RoleAdminChanged",
                "kind": "nested",
            },
            {
                "name": "GovernanceAdminAdded",
                "type": "src::roles_interface::GovernanceAdminAdded",
                "kind": "nested",
            },
            {
                "name": "GovernanceAdminRemoved",
                "type": "src::roles_interface::GovernanceAdminRemoved",
                "kind": "nested",
            },
            {
                "name": "UpgradeGovernorAdded",
                "type": "src::roles_interface::UpgradeGovernorAdded",
                "kind": "nested",
            },
            {
                "name": "UpgradeGovernorRemoved",
                "type": "src::roles_interface::UpgradeGovernorRemoved",
                "kind": "nested",
            },
        ],
    },
]


types = ["core::starknet::contract_address::ContractAddress", "core::integer::u256"]

caller_address = "0x37bbb23e3414fd67d4eb7cde5dccb4b377fe02d4883b5bc8a8fbab35a81d8e9"
class_hash = "0x5ffbcfeb50d200a0677c48a129a11245a3fc519d1d98d76882d1c9a1b19c6ed"


# def test_decode_erc20_eth_transfer():
#     decoded_transfer = decode_from_types(types, calldata)
#     assert len(decoded_transfer) == 2
#     assert (
#         decoded_transfer[0]
#         == "0x07916596feab669322f03b6df4e71f7b158e291fd8d273c0e53759d5b7240b4a"
#     )
#     assert decoded_transfer[1] == 4900746299664880
#
#     decoded_result = decode_from_types(["core::bool"], ["0x1"])
#     assert decoded_result[0]
#     assert len(decoded_result) == 1


eth_tuple = {
    "components": [
        {
            "internalType": "enum LibSignature.SignatureType",
            "name": "signatureType",
            "type": "uint8",
        },
        {"internalType": "uint8", "name": "v", "type": "uint8"},
        {"internalType": "bytes32", "name": "r", "type": "bytes32"},
        {"internalType": "bytes32", "name": "s", "type": "bytes32"},
    ],
    "internalType": "struct LibSignature.Signature[]",
    "name": "signatures",
    "type": "tuple[]",
}
