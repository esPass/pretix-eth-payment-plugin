from django.utils.translation import ugettext_lazy as _

ETH = "ETH"
DAI = "DAI"


def make_erc_681_url(
    to_address, payment_amount, chain_id=1, is_token=False, token_address=None
):
    """Make ERC681 URL based on if transferring ETH or a token like DAI and the chain id"""
    if is_token:
        if token_address == None:
            raise ValueError(
                "if is_token is true, then you must pass contract address of the token."
            )  # noqa: E501

        return f"ethereum:{token_address}@{chain_id}/transfer?address={to_address}&uint256={payment_amount}"  # noqa: E501
    # if ETH (not token)
    return f"ethereum:{to_address}@{chain_id}?value={payment_amount}"


def make_uniswap_url(
    output_currency, recipient_address, exact_amount, input_currency=None
):
    """
    Build uniswap url to swap exact_amount of one currency to another and send to a address.
    Input currency may not be fixed but output_currency must be provided.
    """
    url = f"https://uniswap.exchange/send?exactField=output&exactAmount={exact_amount}&outputCurrency={output_currency}&recipient={recipient_address}"  # noqa: E501

    if input_currency == None:
        return url

    # else - swap between a fixed currency to another:
    return url + f"&inputCurrency={input_currency}"


class INetwork(object):
    """Interface that creates basic functionality to plug network into payments.py"""

    identifier = None
    verbose_name = None
    eth_currency_choice = ()
    dai_currency_choice = ()

    def __init__(self):
        if not (self.identifier and self.verbose_name):
            raise ValueError(
                "identifier and verbose_name class variable must be specified."
            )
        eth_currency = f"{ETH}-{self.verbose_name}"
        dai_currency = f"{DAI}-{self.verbose_name}"
        self.eth_currency_choice = ((eth_currency, _(eth_currency)),)
        self.dai_currency_choice = ((dai_currency, _(dai_currency)),)

    def payment_instructions(
        self, wallet_address, payment_amount, amount_in_ether_or_dai, currency_type
    ):
        """
        Instructions on how to pay in this network

        :param wallet_address: address to pay to
        :param payment_amount: amount to pay (in wei)
        :param amount_in_ether_or_dai: amount to pay (from_wei(payment_amount))
        :param currency_type: ETH or DAI?
        :returns dictionary with relevant information like
                'erc_681_url', 'uniswap_url', 'web3modal_url',
                'amount_manual' (amount + 'ETH/DAI'), 'wallet_address'
        """

        raise NotImplementedError(
            "This method has not yet been implemented for the network"
        )


class Rinkeby(INetwork):
    """Implementation for Rinkeby Testnet"""

    identifier = "Rinkeby"
    verbose_name = "Rinkeby Ethereum Testnet"
    CHAIN_ID = 4
    DAI_ADDRESS = "0xc7AD46e0b8a400Bb3C915120d284AafbA8fc4735"

    def payment_instructions(
        self, wallet_address, payment_amount, amount_in_ether_or_dai, currency_type
    ):
        """
        Instructions for paying ETH or DAI in Rinkeby. Pay via a web3 modal, ERC 681 (QR Code), uniswap url or manually.
        """
        if currency_type == "ETH":
            erc_681_url = make_erc_681_url(
                wallet_address, payment_amount, self.CHAIN_ID
            )
            amount_manual = f"{amount_in_ether_or_dai} ETH"
            uniswap_url = make_uniswap_url(
                ETH, wallet_address, amount_in_ether_or_dai, self.DAI_ADDRESS
            )
        elif currency_type == "DAI":
            erc_681_url = make_erc_681_url(
                wallet_address,
                payment_amount,
                self.CHAIN_ID,
                is_token=True,
                token_address=self.DAI_ADDRESS,
            )
            amount_manual = f"{amount_in_ether_or_dai} DAI"
            uniswap_url = make_uniswap_url(
                self.DAI_ADDRESS, wallet_address, amount_in_ether_or_dai
            )
        else:
            raise ImproperlyConfigured(
                f"Unrecognized currency: {currency_type}"
            )  # noqa: E501

        web3modal_url = f"https://checkout.web3modal.com/?currency={currency_type}&amount={amount_in_ether_or_dai}&to={wallet_address}"  # noqa: E501

        return {
            "erc_681_url": erc_681_url,
            "uniswap_url": uniswap_url,
            "web3modal_url": web3modal_url,
            "amount_manual": amount_manual,
            "wallet_address": wallet_address,
        }


class L1(INetwork):
    """Implementation for Ethereum L1"""

    identifier = "L1"
    verbose_name = "Ethereum"
    DAI_ADDRESS = "0x6b175474e89094c44da98b954eedeac495271d0f"

    def payment_instructions(
        self, wallet_address, payment_amount, amount_in_ether_or_dai, currency_type
    ):  # noqa: E501
        """
        Instructions for paying ETH or DAI in L1 Ethereum. Pay via a web3 modal, ERC 681 (QR Code), uniswap url or manually.
        """
        if currency_type == "ETH":
            erc_681_url = make_erc_681_url(wallet_address, payment_amount)
            amount_manual = f"{amount_in_ether_or_dai} ETH"
            uniswap_url = make_uniswap_url(
                ETH, wallet_address, amount_in_ether_or_dai, self.DAI_ADDRESS
            )
        elif currency_type == "DAI":
            erc_681_url = make_erc_681_url(
                wallet_address,
                payment_amount,
                is_token=True,
                token_address=self.DAI_ADDRESS,
            )
            amount_manual = f"{amount_in_ether_or_dai} DAI"
            uniswap_url = make_uniswap_url(
                self.DAI_ADDRESS, wallet_address, amount_in_ether_or_dai
            )

        else:
            raise ImproperlyConfigured(f"Unrecognized currency: {currency_type}")

        web3modal_url = f"https://checkout.web3modal.com/?currency={currency_type}&amount={amount_in_ether_or_dai}&to={wallet_address}"  # noqa: E501

        return {
            "erc_681_url": erc_681_url,
            "uniswap_url": uniswap_url,
            "web3modal_url": web3modal_url,
            "amount_manual": amount_manual,
            "wallet_address": wallet_address,
        }


class ZkSync(INetwork):
    """Implementation for ZkSync"""

    identifier = "ZkSync"
    verbose_name = "ZkSync"


all_networks = [L1, Rinkeby, ZkSync]
all_network_ids_to_networks = {}
all_network_verbose_names_to_ids = {}

for network in all_networks:
    all_network_ids_to_networks[network.identifier] = network()
    all_network_verbose_names_to_ids[network.verbose_name] = network.identifier
