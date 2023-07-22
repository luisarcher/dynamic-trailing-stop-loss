

from dtsl.config import Config


class Strategy:

    def __init__(self, lot_size_filter: dict) -> None:
        
        # Used to calculate TP and Exit prices
        self.lot_size_filter = lot_size_filter

        self.config = Config()
        self.stop_loss_multiplier = float(self.config.get_config_value("strategy").get("stop_loss_multiplier"))

        # Main params
        # 2:1 R2RR
        self.conf_tp_perc = 0.04 # 4%
        self.conf_sl_perc = 0.02 # 2%
        #self.conf_min_tsl = 0.0025
        self.conf_sl_min_gap = 0.0035

        # Runtime state values
        self.previous_sl_price = 0.0
        self.max_price = 0.0

    def get_tp_price(self, side: str, entry_price: float) -> float:
        """
        Calculate the take profit price based on the side and entry price.

        Args:
            side (str): The counter side of the original position ('BUY' for SHORT, 'SELL' for LONG).
            entry_price (float): The entry price of the original position.

        Returns:
            float: The take profit price adjusted based on the configured take profit percentage and lot size filter.
        """

        if side.upper() == 'BUY':
            # Calculate take profit price for SHORT position
            order_price = entry_price * (1 - self.conf_tp_perc)
        elif side.upper() == 'SELL':
            # Calculate take profit price for LONG position
            order_price = entry_price * (1 + self.conf_tp_perc)
        # Adjust price based on lot size filter
        order_price = Strategy.round_to_tick_size(order_price, self.lot_size_filter)
        return order_price

    def get_sl_price(self, counter_side: str, entry_price: float) -> float:
        """
        Calculate the stop loss price based on the side and entry price.

        Args:
            side (str): The counter side of the original position ('BUY' for SHORT, 'SELL' for LONG).
            entry_price (float): The entry price of the original position.

        Returns:
            float: The stop loss price adjusted based on the configured stop loss percentage and lot size filter.
        """
        if counter_side.upper() == 'BUY':
            # Calculate stop loss price for SHORT position
            order_price = entry_price * (1 + self.conf_sl_perc)
        elif counter_side.upper() == 'SELL':
            # Calculate stop loss price for LONG position
            order_price = entry_price * (1 - self.conf_sl_perc)
        # Adjust price based on lot size filter
        order_price = Strategy.round_to_tick_size(order_price, self.lot_size_filter)
        self.previous_sl_price = order_price
        return order_price
    
    def update_sl_price(self, side: str, entry_price: float, current_price: float) -> float:
        """
        Calculate the stop loss price based on the side and entry price.

        Args:
            side (str): The counter side of the original position ('BUY' for SHORT, 'SELL' for LONG).
            entry_price (float): The entry price of the original position.

        Returns:
            float: The stop loss price adjusted based on the configured stop loss percentage and lot size filter.
        """
        if side.upper() == 'BUY':
            # Calculate stop loss price for SHORT position
            order_price = self.drag_short_stop_loss(float(entry_price), float(current_price))
        elif side.upper() == 'SELL':
            # Calculate stop loss price for LONG position
            order_price = self.drag_long_stop_loss(float(entry_price), float(current_price))
        
        # To be ignored, we are not dragging the SL
        if order_price == 0.0:
            return 0.0
        
        # Adjust price based on lot size filter
        order_price = Strategy.round_to_tick_size(order_price, self.lot_size_filter)
        #self.previous_sl_price = order_price
        return order_price

    @staticmethod
    def round_to_tick_size(price: float, lot_size_filter: dict) -> float:
        tick_size = float(lot_size_filter['filters'][0]['tickSize'])
        max_precision = lot_size_filter['pricePrecision']

        # Calculate the scale factor based on the maximum precision
        scale_factor = 10 ** max_precision

        # Round the price to the nearest tick size and adjust the precision
        rounded_price = round(price / tick_size) * tick_size
        adjusted_price = round(rounded_price * scale_factor) / scale_factor
        return adjusted_price


    def drag_long_stop_loss(self, entry_price: float, current_price: float) -> float:

        # UC: Negative profit, don't drag SL
        if current_price < entry_price:
            # Do not drag SL
            return 0.0
        
        if current_price > self.max_price:
            # Calculate the divergence from the previous max price
            #  i.e. how the current price superseded the max price
            #  example: current 1.012, max: 1.0, then divergence = 0.012
            price_divergence_float = (current_price - self.max_price)

            # Update the max_price as it is now the max
            self.max_price = current_price

            # Don't ask me about 1.85, it just felt like the right number
            sl_order_price = (price_divergence_float * self.stop_loss_multiplier) + self.previous_sl_price

            # Check if the current stop loss price does not surpass current_price + tolerance
            #  Let's say a symbol is trading at 2.00, if we set a min gap of 0.01, then SL price cannot be higher than 1.98.
            if sl_order_price > ((1-self.conf_sl_min_gap) * current_price):
                return 0.0
            
            self.previous_sl_price = sl_order_price
            return self.previous_sl_price
        return 0.0

    def drag_short_stop_loss(self, entry_price: float, current_price: float) -> float:

        # UC: Negative profit, don't drag SL
        if current_price > entry_price:
            # Do not drag SL
            return 0.0
        
        # Since we are Shorting, we can look at max_price as the maximum lower price
        if current_price < self.max_price:
            # Calculate the divergence from the previous max price
            #  i.e. how the current price superseded the max price
            #  example: current 0.988, max: 1.0, then divergence = -0.012
            price_divergence_float = (current_price - self.max_price)

            # Update the max_price as it is now the max
            self.max_price = current_price

            # Don't ask me about 1.85, it just felt like the right number
            sl_order_price = (price_divergence_float * self.stop_loss_multiplier) + self.previous_sl_price

            # Check if the current stop loss price does not surpass current_price + tolerance
            #  Let's say a symbol is trading at 2.00, if we set a min gap of 0.01, then SL price cannot be lower than 2.02.
            if sl_order_price < ((1+self.conf_sl_min_gap) * current_price):
                return 0.0
            self.previous_sl_price = sl_order_price
            return self.previous_sl_price
        return 0.0