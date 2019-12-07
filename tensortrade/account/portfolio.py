import pandas as pd

from typing import Union, List, Dict

from tensortrade import Component


class Portfolio(Component):
    """A account of wallets for use on an Exchange."""

    registered_name = "account"

    def __init__(self):
        self._base_instrument = self.context.base_instrument
        self._wallets = {}

    @property
    def base_instrument(self) -> 'Instrument':
        """The exchange instrument used to measure value and performance statistics."""
        return self._base_instrument

    @base_instrument.setter
    def base_instrument(self, base_instrument: 'Instrument'):
        self._base_instrument = base_instrument

    @property
    def initial_balance(self) -> float:
        """The initial balance of the base instrument on the exchange."""
        raise NotImplementedError

    @property
    def balance(self) -> float:
        """The current balance of the base instrument on the exchange."""
        raise NotImplementedError

    @property
    def balances(self) -> Dict['Instrument', float]:
        """The current balance of each instrument on the exchange (non-positive balances excluded)."""
        raise NotImplementedError

    @property
    def performance(self) -> pd.DataFrame:
        """The performance of the active account on the exchange since the last reset."""
        raise NotImplementedError

    @property
    def instrument_balance(self, symbol: str) -> float:
        """The current balance of the specified symbol on the exchange, denoted in the base instrument.

        Arguments:
            symbol: The symbol to retrieve the balance of.

        Returns:
            The balance of the specified exchange symbol, denoted in the base instrument.
        """
        wallets = self._wallets

        if symbol in wallets.keys():
            return wallets[symbol]

        return 0

    def group_by_exchange(self):
        pass

    @property
    def net_worth(self) -> float:
        """Calculate the net worth of the active account on the exchange.

        Returns:
            The total account value of the active account on the exchange.
        """
        net_worth = self.balance
        wallets = self._wallets

        if not wallets:
            return net_worth

        for symbol, wallet in wallets.items():
            if symbol == self._base_instrument:
                continue

            current_price = self._exchange.current_price(symbol=symbol)
            net_worth += current_price * wallet.balance

        return net_worth

    @property
    def profit_loss_percent(self) -> float:
        """Calculate the percentage change in net worth since the last reset.

        Returns:
            The percentage change in net worth since the last reset.
        """
        return 100 * float(self.net_worth / self.initial_balance)

    def get_wallet(self, exchange_id: str, instrument: 'Instrument'):
        return self._wallets[(exchange_id, instrument)]

    def add(self, wallet: 'Wallet'):
        k = (str(wallet.exchange.id), wallet.instrument)
        self._wallets[k] = wallet

    def remove(self, wallet: 'Wallet'):
        del self._wallets[(str(wallet.exchange.id), wallet.instrument)]