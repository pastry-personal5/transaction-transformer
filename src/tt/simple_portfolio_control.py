import datetime
import os
from typing import Optional

from loguru import logger

import tt.investing_dot_com_text_exporter

from tt.fact_data_control import FactDataControl
from tt.simple_portfolio import SimplePortfolio
from tt.simple_transaction import SimpleTransaction
from tt.yahoo_finance_web_exporter import YahooFinanceWebExporter


class SimplePortfolioControl:

    def __init__(self, fact_data_control: FactDataControl):
        self.fact_data_control = fact_data_control  # It's a reference to a `control`

    def _apply_stock_split(
        self, portfolio_snapshot_date: datetime.date, p: SimplePortfolio
    ):
        const_symbol_namespace = "NASDAQ"
        p_dict = p.p
        for symbol in p_dict:
            # Get a list[StockSplit]
            list_of_stock_split = self.fact_data_control.stock_split_control.get_all_filtered_by_symbol_and_symbol_namespace(
                symbol, const_symbol_namespace
            )
            if len(list_of_stock_split) <= 0:
                continue
            for s in list_of_stock_split:
                event_date = s.event_date
                if event_date > portfolio_snapshot_date:
                    numerator = s.numerator
                    denominator = s.denominator
                    p_dict[symbol]["amount"] = (
                        p_dict[symbol]["amount"] * numerator / denominator
                    )
                    p_dict[symbol]["open_price"] = (
                        p_dict[symbol]["open_price"] * denominator / numerator
                    )
                    logger.info(
                        f"Found Stock Split on ({event_date}). numerator({numerator}) denominator({denominator}) amount({p_dict[symbol]['amount']}) open_price({p_dict[symbol]['open_price']})"
                    )

    def build_portfolio(
        self,
        list_of_simple_transactions: list[SimpleTransaction],
        portfolio_snapshot_date: Optional[datetime.date],
    ):
        p = SimplePortfolio()
        for transaction in list_of_simple_transactions:
            # If `portfolio_snapshot_date` is given.
            if portfolio_snapshot_date:
                if transaction.open_date > portfolio_snapshot_date:
                    continue
            p.record(transaction)

        if portfolio_snapshot_date:
            self._apply_stock_split(portfolio_snapshot_date, p)
        return p

    def do_investing_dot_com_portfolio_export(self, portfolio: SimplePortfolio) -> None:
        try:
            from tt.constants import Constants
            output_file_path = os.path.join(Constants.output_data_dir_path, "investing_dot_com_portfolio.txt")
            f = open(output_file_path, "w", encoding="utf-8")
            tt.investing_dot_com_text_exporter.do_investing_dot_com_file_export_to_file(
                f, portfolio
            )
            f.close()
        except IOError as e:
            logger.error(f"IOError: {e}")
            logger.error("The file path was: %s" % output_file_path)

    def do_yahoo_finance_web_export(self, portfolio):
        from tt.constants import Constants
        module_config_file_path = os.path.join(Constants.config_dir_path, "yahoo.yaml")
        yahoo_finance_web_exporter = YahooFinanceWebExporter()
        if not yahoo_finance_web_exporter.read_config(module_config_file_path):
            return False
        if not yahoo_finance_web_exporter.verify_config():
            return False
        yahoo_finance_web_exporter.prepare_export()
        yahoo_finance_web_exporter.export_simple_portfolio(portfolio)
        yahoo_finance_web_exporter.cleanup()
        return True
