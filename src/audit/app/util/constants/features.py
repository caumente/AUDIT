class Features:
    def __init__(self):

        self.categories = ['Statistical', 'Texture', 'Spatial', 'Tumor']

        self.common = {
            'subject ID': 'ID'
        }

        self.longitudinal = {
            'ID': 'longitudinal_id',
            'Time point': 'time_point'
        }

        self.statistical = {
            'Max. intensity (T1)': 't1_max_intensity',
            'Max. intensity (T1ce)': 't1ce_max_intensity',
            'Max. intensity (T2)': 't2_max_intensity',
            'Max. intensity (FLAIR)': 'flair_max_intensity',
            'Min. intensity (T1)': 't1_min_intensity',
            'Min. intensity (T1ce)': 't1ce_min_intensity',
            'Min. intensity (T2)': 't2_min_intensity',
            'Min. intensity (FLAIR)': 'flair_min_intensity',
            'Mean intensity (T1)': 't1_mean_intensity',
            'Mean intensity (T1ce)': 't1ce_mean_intensity',
            'Mean intensity (T2)': 't2_mean_intensity',
            'Mean intensity (FLAIR)': 'flair_mean_intensity',
            "Median intensity (T1)": "t1_median_intensity",
            "Median intensity (T1ce)": "t1ce_median_intensity",
            "Median intensity (T2)": "t2_median_intensity",
            "Median intensity (FLAIR)": "flair_median_intensity",
            'Std. intensity (T1)': 't1_std_intensity',
            'Std. intensity (T1ce)': 't1ce_std_intensity',
            'Std. intensity (T2)': 't2_std_intensity',
            'Std. intensity (FLAIR)': 'flair_std_intensity',
            '10th-Percentile (T1) ': 't1_10_perc_intensity',
            '10th-Percentile (T1ce) ': 't1ce_10_perc_intensity',
            '10th-Percentile (T2) ': 't2_10_perc_intensity',
            '10th-Percentile (FLAIR) ': 'flair_10_perc_intensity',
            '90th-Percentile (T1) ': 't1_90_perc_intensity',
            '90th-Percentile (T1ce) ': 't1ce_90_perc_intensity',
            '90th-Percentile (T2) ': 't2_90_perc_intensity',
            '90th-Percentile (FLAIR) ': 'flair_90_perc_intensity',
            'Intensity range (T1)': 't1_range_intensity',
            'Intensity range (T1ce)': 't1ce_range_intensity',
            'Intensity range (T2)': 't2_range_intensity',
            'Intensity range (FLAIR)': 'flair_range_intensity',
            'Skewness (T1)': 't1_skewness',
            'Skewness (T1ce)': 't1ce_skewness',
            'Skewness (T2)': 't2_skewness',
            'Skewness (FLAIR)': 'flair_skewness',
            'Kurtosis (T1)': 't1_kurtosis',
            'Kurtosis (T1ce)': 't1ce_kurtosis',
            'Kurtosis (T2)': 't2_kurtosis',
            'Kurtosis (FLAIR)': 'flair_kurtosis',
        }

        self.spatial = {
            'Axial dim.': 'axial_dim',
            'Coronal dim.': 'coronal_dim',
            'Sagittal dim.': 'sagittal_dim',
            'Brain CM (Axial)': 'axial_brain_centre_mass',
            'Brain CM (Coronal)': 'coronal_brain_centre_mass',
            'Brain CM (Sagittal)': 'sagittal_brain_centre_mass'
        }

        self.tumor = {
            'No. tumor slices (Axial)': 'axial_tumor_slices',
            'No. tumor slices (Coronal)': 'coronal_tumor_slices',
            'No. tumor slices (Sagittal)': 'sagittal_tumor_slices',
            'Lower tumor slice (Axial)': 'min_axial_tumor_slice',
            'Upper tumor slice (Axial)': 'max_axial_tumor_slice',
            'Lower tumor slices (Coronal)': 'min_coronal_tumor_slice',
            'Upper tumor slice (Coronal)': 'max_coronal_tumor_slice',
            'Lower. tumor slices (Sagittal)': 'min_sagittal_tumor_slice',
            'Upper tumor slice (Sagittal)': 'max_sagittal_tumor_slice',
            'Lesion size (ENH)': 'lesion_size_enh',
            'Lesion size (EDE)': 'lesion_size_ede',
            'Lesion size (NEC)': 'lesion_size_nec',
            'Lesion size': 'lesion_size',
            'Tumor location (All labels)': 'whole_tumor_location',
            'Tumor location (ENH)': 'enh_tumor_location',
            'Tumor location (EDE)': 'ede_tumor_location',
            'Tumor location (NEC)': 'nec_tumor_location',
            'Tumor CM (Whole Axial)': 'axial_whole_center_mass',
            'Tumor CM (Whole Coronal)': 'coronal_whole_center_mass',
            'Tumor CM (Whole Sagittal)': 'sagittal_whole_center_mass',
            'Tumor CM (ENH Axial)': 'axial_enh_center_mass',
            'Tumor CM (ENH Coronal)': 'coronal_enh_center_mass',
            'Tumor CM (ENH Sagittal)': 'sagittal_enh_center_mass',
            'Tumor CM (EDE Axial)': 'axial_ede_center_mass',
            'Tumor CM (EDE Coronal)': 'coronal_ede_center_mass',
            'Tumor CM (EDE Sagittal)': 'sagittal_ede_center_mass',
            'Tumor CM (NEC Axial)': 'axial_nec_center_mass',
            'Tumor CM (NEC Coronal)': 'coronal_nec_center_mass',
            'Tumor CM (NEC Sagittal)': 'sagittal_nec_center_mass',
        }

        self.texture = {
            'Mean contrast (T1)': 't1_mean_contrast',
            'Mean contrast (T1ce)': 't1ce_mean_contrast',
            'Mean contrast (T2)': 't2_mean_contrast',
            'Mean contrast (FLAIR)': 'flair_mean_contrast',
            'Std contrast (T1)': 't1_std_contrast',
            'Std contrast (T1ce)': 't1ce_std_contrast',
            'Std contrast (T2)': 't2_std_contrast',
            'Std contrast (FLAIR)': 'flair_std_contrast',
            'Mean correlation (T1)': 't1_mean_correlation',
            'Mean correlation (T1ce)': 't1ce_mean_correlation',
            'Mean correlation (T2)': 't2_mean_correlation',
            'Mean correlation (FLAIR)': 'flair_mean_correlation',
            'Std correlation (T1)': 't1_std_correlation',
            'Std correlation (T1ce)': 't1ce_std_correlation',
            'Std correlation (T2)': 't2_std_correlation',
            'Std correlation (FLAIR)': 'flair_std_correlation',
            'Mean dissimilarity (T1)': 't1_mean_dissimilarity',
            'Mean dissimilarity (T1ce)': 't1ce_mean_dissimilarity',
            'Mean dissimilarity (T2)': 't2_mean_dissimilarity',
            'Mean dissimilarity (FLAIR)': 'flair_mean_dissimilarity',
            'Std dissimilarity (T1)': 't1_std_dissimilarity',
            'Std dissimilarity (T1ce)': 't1ce_std_dissimilarity',
            'Std dissimilarity (T2)': 't2_std_dissimilarity',
            'Std dissimilarity (FLAIR)': 'flair_std_dissimilarity',
            'Mean energy (T1)': 't1_mean_energy',
            'Mean energy (T1ce)': 't1ce_mean_energy',
            'Mean energy (T2)': 't2_mean_energy',
            'Mean energy (FLAIR)': 'flair_mean_energy',
            'Std energy (T1)': 't1_std_energy',
            'Std energy (T1ce)': 't1ce_std_energy',
            'Std energy (T2)': 't2_std_energy',
            'Std energy (FLAIR)': 'flair_std_energy',
            'Mean homogeneity (T1)': 't1_mean_homogeneity',
            'Mean homogeneity (T1ce)': 't1ce_mean_homogeneity',
            'Mean homogeneity (T2)': 't2_mean_homogeneity',
            'Mean homogeneity (FLAIR)': 'flair_mean_homogeneity',
            'Std homogeneity (T1)': 't1_std_homogeneity',
            'Std homogeneity (T1ce)': 't1ce_std_homogeneity',
            'Std homogeneity (T2)': 't2_std_homogeneity',
            'Std homogeneity (FLAIR)': 'flair_std_homogeneity',
            'Mean ASM (T1)': 't1_mean_ASM',
            'Mean ASM (T1ce)': 't1ce_mean_ASM',
            'Mean ASM (T2)': 't2_mean_ASM',
            'Mean ASM (FLAIR)': 'flair_mean_ASM',
            'Std ASM (T1)': 't1_std_ASM',
            'Std ASM (T1ce)': 't1ce_std_ASM',
            'Std ASM (T2)': 't2_std_ASM',
            'Std ASM (FLAIR)': 'flair_std_ASM'
        }

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

    def get_multiple_features(self, categories):
        features = {}
        for category in categories:
            category_lower = category.lower()
            if hasattr(self, category_lower):
                features.update(getattr(self, category_lower))
        return features
