class Features:
    def __init__(self, config):
        self.sequences = (
            ["T1", "T1ce", "T2", "FLAIR"]
            if config is None
            else [s[1:] if s.startswith("_") else s for s in config.get("sequences")]
        )
        self.lesion_regions = list(config.get("labels").keys())
        self.planes = ["Axial", "Coronal", "Sagittal"]
        self.categories = ["Statistical", "Texture", "Spatial", "Tumor"]
        self.metadata_cols = config.get("metadata_cols", [])

        self.common = {"subject ID": "ID"}

        self.longitudinal = {"ID": "longitudinal_id", "Time point": "time_point"}

        self.statistical = self._generate_statistical_features()
        self.spatial = self._generate_spatial_features()
        self.tumor = self._generate_tumor_features()
        self.texture = self._generate_texture_features()
        self.metadata = self._generate_metadata_features()
        if self.metadata:
            self.categories.append("Metadata")

    def _generate_statistical_features(self):
        """
        Generate statistical features dynamically based on MRI sequences.
        """
        metrics = [
            "Max. intensity",
            "Min. intensity",
            "Mean intensity",
            "Median intensity",
            "Std. intensity",
            "10th-Percentile intensity",
            "90th-Percentile intensity",
            "Range intensity",
            "Skewness",
            "Kurtosis",
        ]
        return {
            f"{metric} ({sequence})": f"{sequence.lower()}_{metric.lower().replace('.', '').replace(' ', '_').replace('-', '_')}"
            for metric in metrics
            for sequence in self.sequences
        }

    def _generate_spatial_features(self):
        """
        Generate spatial features dynamically based on planes
        """

        features = {f"{dim} plane resolution": f"{dim.lower()}_plane_resolution" for dim in self.planes}
        features.update(
            {f"{plane} plane center of mass": f"{plane.lower()}_plane_center_of_mass" for plane in self.planes}
        )
        return features

    def _generate_texture_features(self):
        """
        Generate texture features dynamically based on MRI sequences, metrics, and texture types.
        """
        metrics = ["Mean", "Std"]
        textures = ["contrast", "correlation", "dissimilarity", "energy", "homogeneity", "ASM"]

        return {
            f"{metric} {texture} ({sequence})": f"{sequence.lower()}_{metric.lower()}_{texture.lower()}"
            for metric in metrics
            for texture in textures
            for sequence in self.sequences
        }

    def _generate_tumor_features(self):
        """
        Generate tumor-related features dynamically based on planes and lesion regions.
        """
        region_renamed = {"BKG": "WHOLE"}
        tumor_features = {}

        tumor_features.update(
            {
                f"Number of tumor slices ({plane})": f"{plane.lower()}_tumor_slices".replace(" ", "_")
                for plane in self.planes
            }
        )

        tumor_features.update(
            {
                f"{slice_type} tumor slice ({plane})": f"{slice_type.lower()}_{plane.lower()}_tumor_slice".replace(
                    " ", "_"
                )
                for plane in self.planes
                for slice_type in ["Lower", "Upper"]
            }
        )

        tumor_features.update(
            {
                f"Lesion size ({region_renamed.get(region, region)})": f"lesion_size_{region_renamed.get(region, region).lower()}"
                for region in self.lesion_regions
            }
        )

        tumor_features.update(
            {
                f"Tumor location ({region_renamed.get(region, region)})": f"{region_renamed.get(region, region).lower()}_tumor_location"
                for region in self.lesion_regions
            }
        )

        tumor_features.update(
            {
                f"{plane} plane tumor center of mass ({region_renamed.get(region, region)})": f"{plane.lower()}_{region_renamed.get(region, region).lower()}_center_mass".replace(
                    " ", "_"
                )
                for region in self.lesion_regions
                for plane in self.planes
            }
        )

        return tumor_features

    def _generate_metadata_features(self):
        """
        Load explicitly defined metadata columns from the config file.
        """
        if not self.metadata_cols:
            return {}
        return {col: col for col in self.metadata_cols}

    def get_features(self, category):
        if category == "Statistical":
            return self.statistical
        elif category == "Texture":
            return self.texture
        elif category == "Spatial":
            return self.spatial
        elif category == "Tumor":
            return self.tumor
        elif category == "common":
            return self.common
        elif category == "Metadata":
            return self.metadata
        return None

    def get_multiple_features(self, categories):
        features = {}
        for category in categories:
            category_lower = category.lower()
            if hasattr(self, category_lower):
                features.update(getattr(self, category_lower))
        return features

    def get_pretty_feature_name(self, feature):
        """
        Given an 'ugly' feature name, returns its 'pretty' counterpart by searching through all feature dictionaries.
        """
        # Traverse all feature dictionaries to find the matching value
        for feature_dict in [
            self.common,
            self.longitudinal,
            self.statistical,
            self.spatial,
            self.tumor,
            self.texture,
            self.metadata,
        ]:
            for pretty, ugly in feature_dict.items():
                if ugly == feature:
                    return pretty

        # Return None if no match is found
        return None
