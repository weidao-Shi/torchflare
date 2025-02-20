"""Implements notifiers for slack and discord."""
import json
import os
from abc import ABC

import requests

from torchflare.callbacks.callback import Callbacks
from torchflare.callbacks.states import CallbackOrder


def prepare_data(logs: dict):
    """Function to prepare the data according to the type of message.

    Args:
        logs: Dictionary containing the metrics and loss values.

    Returns:
        string in the same format as logs.
    """
    val = [f"{key} : {value}" for key, value in logs.items()]
    text = "\n".join(val)
    return text


class SlackNotifierCallback(Callbacks, ABC):
    """Class to Dispatch Training progress to your Slack channel."""

    def __init__(self, webhook_url: str):
        """Constructor method for SlackNotifierCallback.

        Args:
            webhook_url : Slack webhook url
        """
        super(SlackNotifierCallback, self).__init__(order=CallbackOrder.EXTERNAL)
        self.webhook_url = webhook_url

    def on_epoch_end(self):
        """This function will dispatch messages to your Slack channel."""
        data = {"text": prepare_data(self.exp.exp_logs)}

        response = requests.post(self.webhook_url, json.dumps(data), headers={"Content-Type": "application/json"})

        if response.status_code != 200:
            raise ValueError(
                "Request to server returned an error {}, the response is:\n{}".format(
                    response.status_code, response.text
                )
            )


class DiscordNotifierCallback(Callbacks, ABC):
    """Class to Dispatch Training progress and plots to your Discord Sever."""

    def __init__(self, exp_name: str, webhook_url: str, send_figures: bool = False):
        """Constructor method for DiscordNotifierCallback.

        Args:
            exp_name : The name of your experiment bot. (Can be anything)
            webhook_url : The webhook url of your discord server/channel.
            send_figures: Whether to send the plots of model history to the server.
        """
        super(DiscordNotifierCallback, self).__init__(order=CallbackOrder.EXTERNAL)
        self.exp_name = exp_name
        self.webhook_url = webhook_url
        self.send_figures = send_figures

    def _find_keys(self, d):

        keys = []
        z = {k: v for k, v in d.items() if k.startswith(self.exp.train_key)}
        for k in z:
            val = k.split("_")[1]
            if val not in keys:
                keys.append(val)

        return keys

    def on_epoch_end(self):
        """On epoch end dispatch per epoch metrics."""
        data = {
            "username": self.exp_name,
            "embeds": [{"description": prepare_data(self.exp.exp_logs)}],
        }
        response = requests.post(self.webhook_url, json.dumps(data), headers={"Content-Type": "application/json"})
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)

    def _create_figs(self):
        keys = self._find_keys(self.exp.history)
        self.exp.plot_history(keys=keys, save_fig=True, plot_fig=False)

    def _send_figs(self):
        self._create_figs()
        data_dict = {}
        for fname in os.listdir(self.exp.plot_dir):
            if ".jpg" in fname:
                data_dict[fname] = open(os.path.join(self.exp.plot_dir, fname), "rb")

        response = requests.post(self.webhook_url, files=data_dict)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)

    def on_experiment_end(self):
        """On experiment end dispatch experiment history plots."""
        if self.send_figures:
            self._send_figs()
