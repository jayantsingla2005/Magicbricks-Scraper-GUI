#!/usr/bin/env python3
"""
Human behavior mimicry helpers
"""
from __future__ import annotations

import random
import time


class BehaviorMimicry:
    """
    Human behavior mimicry for anti-detection
    """

    def __init__(self):
        """Initialize behavior mimicry"""
        self.mouse_patterns = []
        self.typing_patterns = []
        self.scroll_patterns = []
        print("\U0001f916 Behavior Mimicry initialized")

    def human_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0) -> float:
        """Generate human-like delay"""
        mean = (min_seconds + max_seconds) / 2
        std = (max_seconds - min_seconds) / 6  # 99.7% within range
        delay = random.normalvariate(mean, std)
        delay = max(min_seconds, min(max_seconds, delay))
        return delay

    def random_mouse_movement(self, driver):
        """Perform random mouse movements"""
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(driver)
            # Random small movements
            for _ in range(random.randint(2, 5)):
                x_offset = random.randint(-50, 50)
                y_offset = random.randint(-50, 50)
                actions.move_by_offset(x_offset, y_offset)
                actions.pause(random.uniform(0.1, 0.3))
            actions.perform()
        except Exception:
            pass  # Fail silently

    def random_scroll(self, driver):
        """Perform random scrolling"""
        try:
            # Random scroll amount
            scroll_amount = random.randint(100, 500)
            direction = random.choice([1, -1])
            driver.execute_script(f"window.scrollBy(0, {scroll_amount * direction});")
            # Pause after scrolling
            time.sleep(self.human_delay(0.5, 1.5))
        except Exception:
            pass  # Fail silently

    def simulate_reading(self, driver, element=None):
        """Simulate reading behavior"""
        try:
            # Scroll to element if provided
            if element:
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(self.human_delay(0.5, 1.0))
            # Random reading time based on content length
            if element:
                text_length = len(element.text) if element.text else 100
                reading_time = max(1.0, text_length / 200)  # ~200 chars per second
                reading_time += random.uniform(-0.5, 1.0)  # Add variance
            else:
                reading_time = random.uniform(2.0, 5.0)
            time.sleep(reading_time)
        except Exception:
            pass  # Fail silently

