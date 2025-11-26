# BraTS 2024 Tutorial

This tutorial guides you step by step through preparing the BraTS 2024 dataset, organizing it, configuring feature 
extraction, and launching the interactive dashboard to explore your data using the AUDIT framework.

Unlike [BraTS 2025](BraTS_2025.md), this dataset includes a demographic mapping file containing valuable metadata such as glioma type, 
MRI scanner specifications, magnetic field strength, and patient demographics. This enables a deeper analysis—not only 
exploring dataset structure and image-derived features but also uncovering potential biases or acquisition-related 
differences that may affect model performance.

AUDIT provides a unified environment to analyze, compare, and visualize these variations across patient cohorts, 
acquisition sites, and demographic groups.

References:

- [The 2024 Brain Tumor Segmentation (BraTS) Challenge: Glioma Segmentation on Post-treatment MRI](https://arxiv.org/abs/2405.18368)

- [The RSNA-ASNR-MICCAI BraTS 2021 Benchmark on Brain Tumor Segmentation and Radiogenomic Classification](https://arxiv.org/abs/2107.02314)

- [BraTS orchestrator : Democratizing and Disseminating state-of-the-art brain tumor image analysis](https://arxiv.org/abs/2506.13807)


!!! warning

    The [annotation protocol](https://www.synapse.org/Synapse:syn64153130/wiki/631053) followed in this tutorial was: 
    Label 0: Background, Label 1: Non-enhancing tumor core, Label 2: surrounding non-enhancing FLAIR hyperintensity, 
    Label 3: Enhancing tumor, Label 4: resection cavity. However, we encourage users to check the protocol used in their datasets.

---

## 1. Prerequisites

Before starting, make sure you are familiar with the BraTS 2025 tutorial, as this guide assumes you already understand 
the fundamentals of AUDIT, such as environment setup, project structure, and configuration files.

We recommend using an isolated Anaconda environment with Jupyter Notebook and following the same project organization 
used in the previous tutorial.

The BraTS 2024 dataset is hosted on Synapse and **requires prior registration**. Please follow the [official 
instructions](https://www.synapse.org/Synapse:syn64153130/wiki/) from the challenge and to BraTS 2024
[Data Access](https://www.synapse.org/Synapse:syn64377310) section to download the data. 

Once downloaded and unzipped, store the training and additional training sets in a directory called 
`.datasets/BraTS_2024`. The metadata file must be stored in the project root. The project structure should look like 
this before starting:

```
brats2024_project/
├── datasets/
├──── BraTS_2024/
├─────── BraTS-GLI-00005-100/
├─────── BraTS-GLI-00005-101/
├─────── .....
├── config/
├── outputs/
├── logs/
├── BraTS-PTG supplementary demographic information and metadata.xlsx
```


---

## 2. Exploring the metadata

Before working with the imaging data, it is useful to explore the metadata. The BraTS 2024 demographic spreadsheet 
includes variables such as acquisition site, magnetic field strength, scanner manufacturer, patient age, sex, and 
glioma type - all of which can later be used to stratify analyses and investigate dataset heterogeneity.

Let’s begin by loading the file in a pandas DataFrame and take a first look:

```python
import pandas as pd
mapping = pd.read_excel("./BraTS-PTG supplementary demographic information and metadata.xlsx")
mapping.head(4)
```

This will give you a table like this:

| BraTS Subject ID     | Site | Site Subject ID | Annotator 1 | Approver 1 | Train/Test/Validation | Magnetic Field Strength | Manufacturer | Patient's Age | Patient's Sex | Glioma type       |
|----------------------|------|-----------------|-------------|------------|-----------------------|-------------------------|--------------|---------------|---------------|-------------------|
| BraTS-GLI-00005-100  | UCSF | 1002251         | NaN         | AMR        | Train                 | 3.0                     | GE           | 50.0          | M             | Oligodendroglioma |
| BraTS-GLI-00005-101  | UCSF | 1002252         | NaN         | AMR        | Train                 | 3.0                     | GE           | 50.0          | M             | Oligodendroglioma |
| BraTS-GLI-00006-100  | UCSF | 1001751         | BKKF        | JDR        | Train                 | 3.0                     | GE           | 39.0          | F             | Glioblastoma      |
| BraTS-GLI-00006-101  | UCSF | 1001752         | BKKF        | JDR        | Train                 | 3.0                     | GE           | 39.0          | F             | Glioblastoma      |


Each patient record is linked to a specific site and scanner configuration. Later, you can use this information to 
partition the dataset and perform site-wise or scanner-wise analyses.

For this tutorial, we will focus on the training and additional training subsets, excluding validation data.

```python
df = mapping[mapping["Train/Test/Validation "].isin(["Train", "Train-additional"])]
```

## 3. Organizing the dataset by site

To facilitate comparisons between different acquisition centers, we will reorganize the dataset into site-specific 
folders.  The function below automates the process by reading the metadata and copying each subject folder into the 
appropriate subdirectory. However, we  encourage users to perform their own analyses, exploring splitting by glioma 
type, magnetic field strength, manufacturer, and other variables.

The goal is to show how AUDIT can help you better understand your dataset and perform a more accurate evaluation of
segmentation models and MRI cohorts.

Let's create a function to move each patient into their corresponding folder, instead of keeping all of them grouped 
in a single directory.

```python
import os
import shutil

def organize_patients(df, column, input_dir, output_dir):
    """
    Organize patient folders into subfolders based on a DataFrame column.

    Parameters
    ----------
    df : pd.DataFrame
        Metadata DataFrame (must contain 'BraTS Subject ID').
    column : str
        Column name to organize by (e.g., 'Site', 'Manufacturer', 'Glioma type').
    input_dir : str
        Directory containing all patient folders (e.g., 'BraTS_2024').
    output_dir : str
        Directory where organized folders will be created (e.g., 'BraTS_2024_by_site').
    """

    os.makedirs(output_dir, exist_ok=True)

    for _, row in df.iterrows():
        subject = row["BraTS Subject ID"]
        category = str(row[column])  # subfolder name

        # Create category subfolder if it doesn’t exist
        category_folder = os.path.join(output_dir, category)
        os.makedirs(category_folder, exist_ok=True)

        # Source patient folder/file
        subject_path = os.path.join(input_dir, subject)
        dest_path = os.path.join(category_folder, subject)

        if os.path.exists(subject_path):
            if os.path.isdir(subject_path):
                shutil.copytree(subject_path, dest_path, dirs_exist_ok=True)
            else:
                shutil.copy2(subject_path, dest_path)
        else:
            print(f"Subject {subject} not found in {input_dir}")

    print(f"Organization completed in {output_dir}")
```

This function allows you to organize patients into separate directories and can be reused for any other analysis you 
want to perform with the BraTS 2024 dataset. Run the following code to organize your data by acquisition site:

```python
input_dir = "./datasets/BraTS_2024"
output_dir = "./datasets/BraTS_2024_by_site"

organize_patients(df, column="Site", input_dir=input_dir, output_dir=output_dir)
```

Ready! After running this, your project structure will look like:

```
brats2024_project/
├── datasets/
├──── BraTS_2024_by_site/
├────── Duke/
├──────── Duke-02060-100/
├──────── Duke-02060-101/
├──────── .....
├────── Indiana/
├────── Missouri/
├────── UCSD/
├────── UCSF/
├── config/
├── outputs/
├── logs/
├── BraTS-PTG supplementary demographic information and metadata.xlsx
```

To be able to take advantage of all functionalities of AUDIT, for instance the connectivity with ITK-Snap toolkit, we
recommend locating the sequences and masks under the same folder, and predictions for each model under another. Then,
The project structure should be the following.

```
brats2024_project/
├── datasets/
├──── BraTS_2024_by_site/
├────── Duke/
├──────── Duke_images/
├────────── Duke-02060-100/
├────────── Duke-02060-101/
├────────── .....
├──────── Duke_segs/
├────────── model_1/
├──────────── Duke-02060-100_pred.nii.gz
├──────────── Duke-02060-101_pred.nii.gz
├────────── .....
├────────── model_2/
├──────────── Duke-02060-100_pred.nii.gz
├──────────── Duke-02060-101_pred.nii.gz
├────────── .....
├────── Indiana/
├────── Missouri/
├────── UCSD/
├────── UCSF/
├── config/
├── outputs/
├── logs/
├── BraTS-PTG supplementary demographic information and metadata.xlsx
```

## 4. Standardize folder and file naming

As in the BraTS 2025 tutorial, we need to standardize the folder and file names to ensure AUDIT compatibility. This 
includes replacing prefixes, updating sequence identifiers, and ensuring consistent use of underscores. Check
[BraTS 2025 tutorial](BraTS_2025.md) for more details.

### 4.1 Rename folders and files

We’ll first replace the `BraTS-GLI-` prefix with the site name for clarity.

```python
sites = ["Duke", "Indiana", "Missouri", "UCSD", "UCSF"]
for s in sites:
    rename_dirs(
        root_dir=os.path.join(output_dir, s),
        old_name="BraTS-GLI",
        new_name=s,
        safe_mode=False
    )
    
    rename_files(
        root_dir=os.path.join(output_dir, s),
        old_name="BraTS-GLI",
        new_name=s,
        safe_mode=False
    )
```

### 4.2 Standardize sequence

Additionally, to make the sequence names clearer and consistent, we will replace suffixes:

```python
old_names = ['-seg.nii.gz', '-t1c.nii.gz', '-t1n.nii.gz', '-t2f.nii.gz', '-t2w.nii.gz']
new_names = ['_seg.nii.gz', '_t1ce.nii.gz', '_t1.nii.gz', '_flair.nii.gz', '_t2.nii.gz']
sites = ["Duke", "Indiana", "Missouri", "UCSD", "UCSF"]

for s in sites:
    for o, n in zip(old_names, new_names):
        rename_files(
            root_dir=os.path.join(output_dir, s),
            old_name=o,
            new_name=n,
            safe_mode=False
        )
```

### 4.3 Replace dashes with underscores (optional)

Finally, to ensure consistent naming conventions, we replace all `-` characters with `_`:

```python
for s in sites:
    rename_files(root_dir=root_dir=os.path.join(output_dir, s), old_name="-", new_name="_", safe_mode=False)
    rename_dirs(root_dir=root_dir=os.path.join(output_dir, s), old_name="-", new_name="_", safe_mode=False)
```

---

## 5. Run feature extraction

Now that the datasets are ready, let’s configure the feature extraction. AUDIT takes advantage of YAML configuration 
files for extracting features and metrics and running the app. All of them have been created automatically inside 
the `configs/` at the time of generating the project structure. The one we need to edit to run the feature extraction 
is named `feature_extraction.yaml`. 

Here we provide the config file needed for this project. In it, paths to datasets, sequences names, labels mapping, 
features to extract, and output paths need to be defined.:

```yaml
# Paths to all the datasets
data_paths:
  Duke: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/Duke/Duke_images/'
  Indiana: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/Indiana/Indiana_images/'
  Missouri: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/Missouri/Missouri_images/'
  UCSD: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/UCSD/UCSD_images/'
  UCSF: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/UCSF/UCSF_images/'

# Sequences available
sequences:
  - '_t1'
  - '_t2'
  - '_t1ce'
  - '_flair'

# Mapping of labels to their numeric values
labels:
  BKG: 0
  NETC: 1
  SNFH: 2
  ET: 3
  RC: 4

# List of features to extract
features:
  statistical: true
  texture: true
  spatial: true
  tumor: true

# Output paths
output_path: '/home/usr/brats2024_project/outputs/features'
logs_path: '/home/usr/brats2024_project/logs/features'

# Resources
cpu_cores: 4
```

Run feature extraction by using the following command:

```bash
auditapp feature-extraction --config /home/usr/projects/configs/feature_extraction.yaml
```

After execution, `/home/usr/brats2024_project/outputs/features` will contain the extracted features for all the datasets.

!!! danger "Important"
    All paths must be absolute. Otherwise, AUDIT may fall back to its internal default config files.

---

## 6. Launch the dashboard (without predictions)

Once features are extracted, we can explore them using the web app. We should edit the config file named `app.yaml` and 
adapt it as follows:

```yaml
# Sequences available
sequences:
  - '_t1'
  - '_t2'
  - '_t1ce'
  - '_flair'

# Mapping of labels to their numeric values
labels:
  BKG: 0
  NETC: 1
  SNFH: 2
  ET: 3
  RC: 4

# Root paths
datasets_path: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site'
features_path: '/home/usr/brats2024_project/outputs/features'
metrics_path: '/home/usr/brats2024_project/outputs/metrics'

# Raw datasets
raw_datasets:
  Duke: "${datasets_path}/Duke/Duke_images"
  Indiana: "${datasets_path}/Indiana/Indiana_images"
  Missouri: "${datasets_path}/Missouri/Missouri_images"
  UCSD: "${datasets_path}/UCSD/UCSD_images"
  UCSF: "${datasets_path}/UCSF/UCSF_images"

# Feature extraction CSVs
features:
  Duke: "${features_path}/extracted_information_Duke.csv"
  Indiana: "${features_path}/extracted_information_Indiana.csv"
  Missouri: "${features_path}/extracted_information_Missouri.csv"
  UCSD: "${features_path}/extracted_information_UCSD.csv"
  UCSF: "${features_path}/extracted_information_UCSF.csv"


# Metric extraction CSVs
metrics:

# Model predictions
predictions:

```

Launch the app with:

```bash
auditapp run-app --config /home/usr/projects/configs/app.yaml
```

Now it’s time to explore the datasets!

Keep in mind that some feature types may influence generalization across cohorts more than others. For example, while 
the statistical features appear quite similar between the datasets, we encourage you to dive deeper into the data, 
experiment with different feature sets, and challenge your models to reach the next level of performance.

> ![Univariate feature analysis](../assets/tutorials/brats2024_t1_max_intensity_l.png#only-light)
> ![Univariate feature analysis](../assets/tutorials/brats2024_t1_max_intensity_d.png#only-dark)
> *Figure 1:* Univariate feature analysis mode. Maximum pixel intensity distribution for T1 sequence.


If everything has been set up correctly — especially making sure to include the patients (original sequences and masks)
within the dataset_images directory (e.g., datasets/Duke/Duke_images/), and ITK has been installed properly as suggested in the documentation,
then it is possible to click on any of the points of interest and explore them directly in ITK-SNAP.
In our case, we clicked on the patient Indiana-03062-100.


> ![ITK-SNAP by clicking on a point](../assets/tutorials/brats2024_itksnap_l.png#only-light)
> ![ITK-SNAP by clicking on a point](../assets/tutorials/brats2024_itksnap_d.png#only-dark)
> *Figure 2:* Subject Indiana-03062-100 exploration directly on ITK-SNAP by clicking on a point from the boxplot shown in Figure 1.

---


## 7. Perform inference

Ademas de analizar la districucion de los datos, estudiar correlaciones, sujetos anomalos y muchas otras cosas, una de las
funcionalidades principales de AUDIT es la evaluacion de modelos de segmentacion. Para realizar la inferencia, hemos 
hecho uso de los modelos presentados en MICCAI 2025, especificamente de los 4 mejor rankeados en la competicion 
Adult Glioma Segmentation (Pre & Post-Treatment). 

Para ello, nos apoyamos en la libreria [brats](https://github.com/BrainLesion/BraTS) la cual contiene los contenedores 
Docker de cada uno de los modelos:

2025	1st	Ishika Jain, et al.	N/A	❌	BraTS25_1
2025	2nd	Qu Lin, et al.	N/A	✅	BraTS25_2
2025	3rd	Liwei Jin, et al.	N/A	✅	BraTS25_3A
2025	3rd	Adrian Celaya, et al.	N/A	❌	BraTS25_3B


Tras realizar la inferencia sobre los 5 subdatasets (Duke, Indiana, Missouri, UCSD, and UCSF) con cada uno de los 4 modelos,
deberemos tener una estructura de carpetas como la siguiente, por ejemplo para el paciente Duke-02060-100

```
brats2024_project/
├── datasets/
├──── BraTS_2024_by_site/
├────── Duke/
├────── Duke_images/
├────────── Duke-02060-100/
├──────────── Duke-02060-100_flair.nii.gz
├──────────── Duke-02060-100_t1.nii.gz
├──────────── Duke-02060-100_t2.nii.gz
├──────────── Duke-02060-100_t1ce.nii.gz
├──────────── Duke-02060-100_seg.nii.gz
├────────── .....
├────── Duke_seg/
├────────── BraTS25_1/
├──────────── Duke-02060-100/
├────────────── Duke-02060-100_pred.nii.gz
├──────────── .....
├────────── BraTS25_2/
├────────── BraTS25_3A/
├────────── BraTS25_3B/
```

!!! danger "Important"
    Es importante tener en cuenta que las terminaciones *_seg* y *_pred* son palabras reservada dentro de AUDIT y son necesarias
    para poder realizar el calculo de las metricas.

## 8. Run metric extraction

Now that the datasets are ready, let’s configure the metric extraction. al igual que hicimos anteriormente, ahora necesitamos
configurar el archivo de configuracion llamado `metric_extraction.yaml`. 

Here we provide the config file needed para extraer las metricas del dataset Duke. In it, paths to datasets, sequences names, labels mapping, 
features to extract, and output paths need to be defined. El mismo archivo de configuracion deberia prepararse para cada uno de los otros
datasets.

```yaml
# Path to the raw dataset
data_path: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/Duke/Duke_images'

# Paths to model predictions
model_predictions_paths:
  BraTS25_1: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/Duke/Duke_seg/BraTS25_1'
  BraTS25_2: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/Duke/Duke_seg/BraTS25_2'
  BraTS25_3A: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/Duke/Duke_seg/BraTS25_3A'
  BraTS25_3B: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/Duke/Duke_seg/BraTS25_3B'

# Mapping of labels to their numeric values
labels:
  BKG: 0
  NETC: 1
  SNFH: 2
  ET: 3
  RC: 4

# List of metrics to compute
metrics:
  dice: true
  jacc: true
  accu: true
  prec: true
  sens: true
  spec: true
  haus: true
  size: true

# Library used for computing all the metrics
package: audit

# Path where output metrics will be saved
output_path: '/home/usr/brats2024_project/outputs/metrics'
filename: 'Duke'
logs_path: '/home/usr/brats2024_project/logs/metric'

# Resources
cpu_cores: 4
```

Run metric extraction by using the following command:

```bash
auditapp metric-extraction --config /home/usr/projects/configs/metric_extraction.yaml
```

After execution, `/home/usr/brats2024_project/outputs/metrics` will contain the extracted metrics for all the datasets.
    

## 9. Launch the dashboard (with predictions)

Ahora que hemos generado todas las predicciones, tenemos las features y metricas extraidas, podemos relanzar el dashboard
de nuevo tal y como se hizo en el paso 6. Sin embargo, en este caso debemos incluir nuevas lineas en nuestro archivo de configuracion
para que sea capaz de leer las predicciones. 

Aqui proporcionamos la parte restante del archivo de configuracion iniciado en la seccion 6. Los usuarios deberan 
concatenar la informacion de ambos.

```yaml
# Paths for metric extraction CSV files
metrics:
  Duke: "${metrics_path}/extracted_information_Duke.csv"
  Indiana: "${metrics_path}/extracted_information_Indiana.csv"
  Missouri: "${metrics_path}/extracted_information_Missouri.csv"
  UCSD: "${metrics_path}/extracted_information_UCSD.csv"
  UCSF: "${metrics_path}/extracted_information_UCSF.csv"

# Paths for models predictions
predictions:
  Duke:
    BraTS2025_1: "${datasets_path}/Duke/Duke_seg/BraTS25_1"
    BraTS2025_2: "${datasets_path}/Duke/Duke_seg/BraTS25_2"
    BraTS2025_3A: "${datasets_path}/Duke/Duke_seg/BraTS25_3A"
    BraTS2025_3B: "${datasets_path}/Duke/Duke_seg/BraTS25_3B"
  Indiana:
    BraTS2025_1: "${datasets_path}/Indiana/Indiana_seg/BraTS25_1"
    BraTS2025_2: "${datasets_path}/Indiana/Indiana_seg/BraTS25_2"
    BraTS2025_3A: "${datasets_path}/Indiana/Indiana_seg/BraTS25_3A"
    BraTS2025_3B: "${datasets_path}/Indiana/Indiana_seg/BraTS25_3B"
  Missouri:
    BraTS2025_1: "${datasets_path}/Missouri/Missouri_seg/BraTS25_1"
    BraTS2025_2: "${datasets_path}/Missouri/Missouri_seg/BraTS25_2"
    BraTS2025_3A: "${datasets_path}/Missouri/Missouri_seg/BraTS25_3A"
    BraTS2025_3B: "${datasets_path}/Missouri/Missouri_seg/BraTS25_3B"
  UCSD:
    BraTS2025_1: "${datasets_path}/UCSD/UCSD_seg/BraTS25_1"
    BraTS2025_2: "${datasets_path}/UCSD/UCSD_seg/BraTS25_2"
    BraTS2025_3A: "${datasets_path}/UCSD/UCSD_seg/BraTS25_3A"
    BraTS2025_3B: "${datasets_path}/UCSD/UCSD_seg/BraTS25_3B"
  UCSF:
    BraTS2025_1: "${datasets_path}/UCSF/UCSF_seg/BraTS25_1"
    BraTS2025_2: "${datasets_path}/UCSF/UCSF_seg/BraTS25_2"
    BraTS2025_3A: "${datasets_path}/UCSF/UCSF_seg/BraTS25_3A"
    BraTS2025_3B: "${datasets_path}/UCSF/UCSF_seg/BraTS25_3B"
```

Relancemos la app nuevamente:


```bash
auditapp run-app --config /home/usr/projects/configs/app.yaml
```

## 10. Model evaluation

AUDIT presenta diferentes analysis modes para analizar el comportamiento de los modelos, desde granularidades mas 
altas hasta detalles mas finos a nivel de paciente y de region. Algunos de los analisis que podemos realizar son los 
siguientes

### 10.1 Segmentation error matrix

La matriz de segmentacion te permite analizar en detalle cuales de las regiones son las que confunde tu modelo. Es una
pseudo matriz de confusion normalizada a nivel de ground truth. Para mas detalles acerca de como funciona este analysis mode
consultar la [documentacion](./../analysis_modes/segmentation_error.md).


> ![Segmentation error matrix para el dataset Duke y el modelo BraTS2025_1](../assets/tutorials/brats2024_segmentation_matrix_l.png#only-light)
> ![Segmentation error matrix para el dataset Duke y el modelo BraTS2025_1](../assets/tutorials/brats2024_segmentation_matrix_d.png#only-dark)
> *Figure 3:* Segmentation error matrix para el dataset Duke y el modelo BraTS2025_1.

La matriz esta analizada a nivel global, es decir, comprende todos los errores cometidos por el modelo a alto nivel
a lo largo de todo el conjunto de datos. El principal problema que tiene el modelo es confundie el Background con la
region SNFH. Por lo tanto, los desarrolladores deberian poner enfasis en buscar estrategias para minimizar este punto 
debil del modelo. La siguiente region mas frecuente que confunde el modelo es el predecir como Background lo que en 
realidad es RC. Sin embargo, hay que tener en cuenta que esta evaluacion se esta haciendo en porcentaje normalizada 
a nivel de actual region, con lo que hay que entenderlo cuidadosamente.

Si nos centramos en uno de los sujetos concretos, por ejemplo el paciente Duke-02060-100, podemos analizar si ese mismo
patron que se cumple en terminos absolutos:

> ![Segmentation error matrix para el paciente Duke-02060-100 del dataset Duke y el modelo BraTS2025_1](../assets/tutorials/brats2024_segmentation_matrix_patient_l.png#only-light)
> ![Segmentation error matrix para el paciente Duke-02060-100 del dataset Duke y el modelo BraTS2025_1](../assets/tutorials/brats2024_segmentation_matrix_patient_d.png#only-dark)
> *Figure 4:* Segmentation error matrix para el paciente Duke-02060-100 del dataset Duke y el modelo BraTS2025_1.


El comportamiento de confundir Background y SNFH que veiamos que tenia el modelo en terminos generales a nivel de dataset
tambien se cumple en terminos absolutos para este paciente en concreto. Un total de 2,905 voxeles fueron etiquetados
como Bakground cuanto en realidad eran voxeles etiquetados como tumorales por el medico (SNFH). sin embargo, para este paciente
concreto, hay un total de 2,106 voxeles que fueron etiquetados como background nuevamente, pero que pertenecian a la 
region ET.

Es por ello que es muy importante entender, no solo los comportamiento generales del modelo, si no los particulares. Y 
ahora que ya conocemos que para este paciente concreto la region ET fue etiquetada incorrectamente, deberiamos analizar
en detalle las caracteristicas de la MRI de este paciente para ver si existe alguna particularidad en el que haga que esa region sea
especialmente dificil de segmentar.


### 10.2 Single model performance

El analizar el performance del modelo en funcion de diferentes caracteristicas nos permite entender si nuestro modelo
tiene algun tipo de sesgo. Por ejemplo, podemos responder a preguntas tales como, es mi modelo mejor prediciendo tumores
que se encuentras lejos del centro de masas del cerebro, o predice mejor nuestro modelo aquellos tumores pertenecientes
a alguna patologia concreta? Para mas detalles acerca de como funciona este analysis mode consultar 
la [documentacion](./../analysis_modes/single_model.md).

Idealmente, lo que esperariamos tener es un diagrama en el que no visualicemos ninguna tendencia especifica, esto indicara
que no existe sesgo alguno. Eso es precisamente es lo que observamos en la figura sigiente

> ![Single model performance analysis el modelo BraTS2025_1](../assets/tutorials/brats2024_single_model_performance_l.svg#only-light)
> ![Single model performance analysis el modelo BraTS2025_1](../assets/tutorials/brats2024_single_model_performance_d.svg#only-dark)
> *Figure 5:* Analisis del comportamiento del modelo BraTS2025_1 en funcion de la localizacion del tumor para cada uno de los subconjuntos

Como vemos, el modelo ha sido entrenado con unos datos lo suficientemente robustos en terminos de localizacion del tumor
como para no tener problemas con diferentes localizaciones.


!!! note
    Recomendamos que el usuario realice sus propios analisis y obtengas sus propias conclusiones, ya que ciertas correlaciones
    podrian no ser lineales, y transformaciones tales como la logaritmica podrian mostras tendencias ocultas.



### 10.3 Pair-wise model performance

La competicion de BraTS adjudico el tercer puesto a dos modelos diferentes, aqui llamados BraTS25_3A y BraTS25_3A sobre
el conjunto de test privado. Nosotros no disponemos de ello, y estamos evaluando los modelos sobre el propio conjunto 
de entrenamiento. Sin embargo, esto nos es suficientes para nuestro proposito demostrativo.

#### 10.3.1 Pair-wise model performance - Aggregated view

Hagamos una comparacion tomando como baseline model el modelo BraTS25_3A y como benchmark el BraTS25_3A. En nuestro caso,
al tener el dataset dividido por Site, podemos analizar las diferencias invididualmente. Usaremos la metrica Dice por
ser la mas ampliamente reportada en problemas de segmentacion medica.

> ![Pairwise model performance analysis el modelo BraTS2025_3A y 3B](./../assets/tutorials/brats2024_agg_pairwise_model_performance_l.png#only-light)
> ![Pairwise model performance analysis el modelo BraTS2025_3A y 3B](./../assets/tutorials/brats2024_agg_pairwise_model_performance_d.png#only-dark)
> *Figure 6:* Pairwise model performance comparison entre los modelos BraTS3A y BraTS_3B para el subnconjunto Duke.

En promedio, el modelo BraTS 3B consiguio mejorar el perfomance del modelo BraTS 3A hasta un 1.42% para la metrica Dice.
La mejora vino propiciada principalmente por una mejor segmentacion de la region RC, y en menor medida por las regiones
NETC y ET. En cambio, el modelo empeoro su rendimiento para la region SNFH entorno a un 1%.

AUDIT tambien propociona una estimacion de si las diferencias son estadisticamente significativas. Por ejemplo, si elegimos
el subconjunto Missouri, podemos comprobar que las diferencias promedio entre ambos modelos son del 0.09%, es decir,
aparentemente una diferencia minima. Al realizar el test estadisto de Wilcoxon signed-rank debido a la violacion de las
asunciones parametricas, se comprueba que no existen diferencias significativas para rechazar la hipotesis nula. Con lo que
sobre este subconjunto especifico, el comportamiento de ambos modelos es similar.

> ![Pairwise model performance analysis el modelo BraTS2025_3A y 3B](./../assets/tutorials/brats2024_statistical_test_l.png#only-light)
> ![Pairwise model performance analysis el modelo BraTS2025_3A y 3B](./../assets/tutorials/brats2024_statistical_test_d.png#only-dark)
> *Figure 7:* Resultados del test estadistico entre los modelos 3A y 3B para comprobar si las diferencias son estasiticamente significativas.


#### 10.3.4 Pair-wise model performance - Disaggregated view

En general los modelos de inteligencia artificial en el campo de la imagen medica se analizan a alto nivel, es decir,
comparando metricas generales tales como la media o la mediana y a veces ni si quiera se proporciona una medida
de la varianza. Es por ello que es fundamental entender a nivel paciente como se comporta el modelo, porque para algunos
casos especificos el modelo falla, estar seguros que la nueva version del modelo que desarrollamos no solo obtiene mejores
resultados promedio si no que generaliza bien y no comete errores importantes en ciertos pacientes que ya eramos capaces
de segmentar correctamente.

Con AUDIT podemos analizar a nivel paciente el rendimiento de 
los modelos. Podemos obtener un Top-K paciente a analizar ya sea por nombre, por rendimiento del baseline model, del 
benchmark model, ordenar ascentende o descendentemente, etc. Comparemos el rendimiento de los modelos 3A y 3B sobre
el subset UCSF.


> ![Pairwise model performance analysis el modelo BraTS2025_3A y 3B](./../assets/tutorials/brats2024_pairwise_per_patient_l.png#only-light)
> ![Pairwise model performance analysis el modelo BraTS2025_3A y 3B](./../assets/tutorials/brats2024_pairwise_per_patient_l.png#only-dark)
> *Figure 8:* Resultados del de la comparacion entee los modelos 3A y 3B a nivel sujeto.

 
Como puede observarse, el modelo B, nuestro benchmark, a mejorado claramente el resultado obtenido por el modelo baseline A
en los casos UCSF-00005-100 y UCSF-00005-101, pasando de valores de entorno a 0.70 a valores de 0.94. Este mismo ejercicio
deberia hacerse para aquellos pacientes para los cuales se ha tenido uin pero rendimiento, y asi entender cuales son
las debilidades de nuestro modelo. 


---

## 11. Conclusions

A lo largo de este tutorial hemos presentado alguna de las caracteristicas que proporciona AUDIT. No solo permite
analizar diferencias en distribuciones si no que su punto fuerte es la evaluacion de modelo y la comparativa a bajo nivel, 
analisis que a medida pasan desapercibidos cuando se presentan resultados en el campo de la imagen medica.



