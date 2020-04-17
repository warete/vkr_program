from vkr import Vkr
import numpy as np


class TestVkr:
    def setup_class(self):
        self.VkrInstance = Vkr()
        self.VkrInstance.yTest = np.array([0, 0, 0, 0, 1, 0, 1, 1, 0])

    def test_calculate_sensitivity_result_is_from_0_to_1(self):
        result = self.VkrInstance.calculate_sensitivity(np.array([0, 0, 0, 0, 1, 0, 1, 0, 0]))
        assert (0.0 < float(result) < 1.0)

    def test_calculate_sensitivity_result_equal_1(self):
        result = self.VkrInstance.calculate_sensitivity(np.array([0, 0, 0, 0, 1, 0, 1, 1, 0]))
        assert (float(result) == 1.0)

    def test_calculate_specificity_result_is_from_0_to_1(self):
        result = self.VkrInstance.calculate_sensitivity(np.array([0, 0, 0, 0, 1, 0, 1, 0, 0]))
        assert (0.0 < float(result) < 1.0)

    def test_calculate_specificity_result_equal_1(self):
        result = self.VkrInstance.calculate_sensitivity(np.array([0, 0, 0, 0, 1, 0, 1, 1, 0]))
        assert (float(result) == 1.0)
