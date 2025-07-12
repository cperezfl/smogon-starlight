import colorsys
import hashlib

class ColorManager:
    def __init__(self, base_color_map, variation_strength=0.2, brighten_only=False):
        self.base_color_map = base_color_map
        self.variation_strength = variation_strength
        self.brighten_only = brighten_only
        self._cache = {}

    def get_color(self, category, key):
        if (category, key) in self._cache:
            return self._cache[(category, key)]

        base_hex = self.base_color_map.get(category, "#888888")
        variant = self._generate_variant(base_hex, key)
        self._cache[(category, key)] = variant
        return variant

    def _generate_variant(self, hex_color, key):
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        hash_val = int(hashlib.md5(key.encode()).hexdigest(), 16)
        delta = ((hash_val % 1000) / 1000 - 0.5) * 2 * self.variation_strength
        if self.brighten_only:
            delta = abs(delta)
        new_l = min(1.0, max(0.0, l + delta))
        r_new, g_new, b_new = colorsys.hls_to_rgb(h, new_l, s)
        return '#{:02x}{:02x}{:02x}'.format(int(r_new*255), int(g_new*255), int(b_new*255))