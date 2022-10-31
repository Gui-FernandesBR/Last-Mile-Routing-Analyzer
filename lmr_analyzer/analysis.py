__author__ = "Guilherme Fernandes Alves"
__license__ = "Mozilla Public License 2.0"



class analysis:
    def __init__(self, name, routes):
        """_summary_

        Parameters
        ----------
        name : str
            The name of the analysis.
        routes : list
            A list containing the routes of the analysis.

        Returns
        -------
        None
        """
    def __calculate_time_period(self):
        """Calculate the time period of the analysis. This is calculated by finding the minimum and maximum 
        time of all routes.

        May be used in the __init__ method.

        Returns
        -------
        None
        """

        # Initialize the time period extremes
        self.total_start_time = self.routes[0].departure_time
        self.total_end_time = self.routes[0].departure_time

        # Iterate over all routes to find the correct extremes
        for route in self.routes:
            if route.departure_time < self.total_start_time:
                self.total_start_time = route.departure_time
            if route.departure_time > self.total_end_time:
                self.total_end_time = route.departure_time

        # Calculate the time period
        self.time_period = (self.total_start_time, self.total_end_time)
        self.time_period_length = self.total_end_time - self.total_start_time

        return None


        return None
