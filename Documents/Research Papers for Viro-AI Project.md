**Expert** **Report:** **A** **Scientific** **and** **Technical**
**Review** **of** **the** **Viro-Al** **Prototype**

**Executive** **Summary:** **The** **Intellectual** **Blueprint**
**for** **Viro-Al**

The Viro-Al prototype represents a significant and forward-thinking
initiative in the field of computational biology, aiming to accelerate
the drug discovery process through artificial intelligence and machine
learning. This report serves as a comprehensive review of the project's
foundational principles, data architecture, and technological approach.
It validates the core components of the Viro-Al system—mutation
prediction, antidote generation, and 3D simulation—by situating them
within the broader context of a paradigm shift from reactive to
proactive virology. The analysis confirms that the project's
three-pillar data architecture is a sound and necessary foundation for
its multimodal capabilities. However, it also highlights the critical,
non-obvious challenges of data heterogeneity and fragmentation. The
report provides a strategic blueprint, including an expanded data
matrix, and delivers three key recommendations to overcome these
challenges: a focus on a robust Extract, Transform, Load (ETL) pipeline,
the adoption of a hybrid machine learning and molecular docking approach
for lead optimization, and a strategic, multi-tool visualization
strategy. The findings underscore that Viro-Al is not an isolated
experiment but a practical embodiment of a proven and revolutionary
scientific approach, poised to transform global health security.

**1.** **A** **New** **Paradigm** **in** **Drug** **Discovery:** **The**
**Shift** **from** **Reactive** **to** **Proactive** **AI**

The Viro-Al system's ambitious goal of revolutionizing viral threat
management is predicated on its ability to transition from a
traditional, reactive approach to a proactive, predictive one.1 This
intellectual foundation is not a mere marketing claim but is firmly
supported by a fundamental and validated trend in modern virology. The
ineficiencies of traditional pharmaceutical research and development
(R&D) have created a compelling need for this

transformation.

**1.1** **The** **High-Stakes** **Challenge** **of** **Traditional**
**R&D**

Developing a new drug through conventional methods is a slow,
prohibitively expensive, and high-risk endeavor.2 The process typically
takes 13-15 years, with the average R&D investment for a new product
exceeding \$2.5 billion.2 A staggering clinical failure rate means that
less than 10% of candidates that enter Phase I trials ever receive FDA
approval. This costly and time-consuming process is the primary
motivation for the pharmaceutical industry's broad interest in
computational solutions.2 Artificial intelligence and machine learning
offer a compelling alternative by enabling virtual screening, molecular
modeling, and predictive analytics, which can rapidly discover new
molecules, optimize lead compounds, and significantly reduce the time
from viral detection to the development of a viable treatment.3

**1.2** **The** **Foundational** **Principles** **of** **Proactive**
**AI-Driven** **Virology**

The Viro-Al project's mission to "forecast threats and suggest drug
modifications" is a direct application of a major trend in computational
biology.1 A comprehensive review in clinical virology confirms a
field-wide shift from "reactive to proactive diagnosis and management".5
The ability of AI to swiftly process and analyze massive, complex
datasets allows for this paradigm change, enabling real-time
surveillance for effective outbreak management.5 A concrete example of
this principle is the EVEscape tool, an AI system developed by
researchers at Harvard and Oxford, which predicts viral mutations and
new variants before they emerge.6 EVEscape was able to accurately
forecast the most frequent and concerning mutations of SARS-CoV-2 that
occurred during the COVID-19 pandemic, demonstrating the real-world
viability of this proactive approach.6 By leveraging a deep learning
model of evolutionary viral sequences combined with biological and
structural information, EVEscape can anticipate new variants with an
accuracy comparable to experimental methods, but with greater speed and
eficiency.7 The Viro-Al prototype, in its design for proactive mutation
prediction and targeted antidote generation, is therefore a practical
and commercial embodiment of this scientifically validated and
revolutionary approach to global health security.1

**2.** **The** **Foundational** **Pillars:** **Data** **Architecture**
**and** **Acquisition**

**Strategy**

The core of the Viro-Al system is a comprehensive, continuously updated
knowledge base. The project's technical documentation correctly
identifies that its advanced analytical capabilities are predicated on a
strategic partition of a large 30GB dataset into three distinct data
clusters: Genomic, Structural, and Clinical & Pharmaceutical.1 While the
sheer volume of this data presents a challenge, a more complex and
subtle problem lies in its fragmented and heterogeneous nature.

**2.1** **The** **Three-Pillar** **Architecture:** **A** **Multimodal**
**Foundation**

The Viro-Al data architecture is designed to support the system's core
functionalities by integrating information from disparate sources.1

> ● **Genomic** **Data:** This cluster includes raw genetic sequences
> and mutation records from authoritative public repositories like the
> National Center for Biotechnology Information (NCBI) GenBank and the
> Global Initiative on Sharing All Influenza Data (GISAID).1 This data,
> often in
>
> .gb and .fasta formats, forms the basis for the Predictive &
> Analytical Engine to understand a virus's fundamental blueprint and
> forecast its behavior.1
>
> ● **Structural** **Data:** The second pillar houses high-resolution,
> three-dimensional (3D) coordinates of viral proteins and other
> macromolecules.1 Sourced from the canonical RCSB Protein Data Bank
> (PDB) and other databases like VPDB, this data, in
>
> .pdb format, is essential for modeling molecular interactions at an
> atomic level. It is the core input for the Antidote Generation and
> Simulation modules.1
>
> ● **Clinical** **&** **Pharmaceutical** **Data:** This data cluster
> provides the real-world context necessary for the system to validate
> its predictions. It consists of structured reports on treatment
> eficacy, clinical outcomes, and pharmaceutical information.1 Sources
> for this data are highly fragmented, including public health portals
> like the WHO Global Health Observatory (GHO) and ClinicalTrials.gov.1
> This information provides the crucial "ground truth" to correlate
> genetic sequences with health outcomes and assign a quantifiable
> "Deadliness" score.1

**2.2** **The** **Challenge** **Beyond** **Volume:** **Addressing**
**Data** **Heterogeneity** **and** **Bias**

While the 30GB data volume is a significant technical constraint that
necessitates the use of distributed computing frameworks like Dask or
Apache Spark, the project faces a more profound challenge: the
fragmentation and inherent messiness of the data itself.1 Clinical and
pharmaceutical data, in particular, is noted as being "the most complex
to acquire due to its fragmented nature".1 The project documents
correctly identify that while resources like PubMed/PMC are valuable,
they provide abstracts and citations in formats like XML rather than the
structured clinical outcomes needed for training machine learning
models.1 This requires a multi-source ingestion strategy.

This challenge is widely recognized in the field of Computer-Aided Drug
Design (CADD).8 Research confirms that many datasets used for training
AI models in drug discovery are often "proprietary, incomplete, or
biased toward well-studied compounds".8 Similarly, the prediction of
drug-target interactions is complicated by the "lack of true negative
drug-target pairs" in available datasets.9 The project must therefore
prioritize the development of a sophisticated ETL (Extract, Transform,
Load) pipeline to clean, normalize, and integrate disparate data from
these fragmented sources. Without this crucial step, the advanced AI/ML
models cannot be effectively trained, rendering their predictive and
generative capabilities ineffectual.

**2.3** **Strategic** **Data** **Acquisition** **Methods**

The Viro-Al project's recommendation to move away from a manual,
one-by-one download approach and toward programmatic acquisition methods
is a necessary technical decision.1 The use of NCBI's Entrez Programming
Utilities (E-utilities), FTP, and the rsync protocol for bulk data
retrieval aligns with industry best practices for eficiently managing
the scale of the dataset.1 The following table provides a strategic
blueprint that synthesizes all identified data sources, methods, and
their specific relevance to the Viro-Al system's core modules.

**Viro-Al** **Data** **Source** **Matrix:** **Expanded** **and**
**Annotated**

||
||
||
||

||
||
||
||
||

||
||
||
||

||
||
||

**3.** **The** **Predictive** **Engine:** **Forecasting** **Viral**
**Evolution** **and** **Risk**

The Viro-Al system's Predictive & Analytical Engine is a central
component that aims to forecast viral behavior and predict mutations
with an accuracy of over 69% from a virus's initial state.1 This
capability is based on the correlation of a virus's genetic sequences
with its historical clinical outcomes to assign a "Deadliness" score.1
The technical approach for this module is well-aligned with and
validated by current academic research in machine learning and genomics.

**3.1** **The** **Technical** **Foundation:** **ML** **&** **Deep**
**Learning** **in** **Genomic** **Analysis**

The use of machine learning (ML) models to predict viral mutations is a
scientifically sound approach that has been successfully applied to
viruses such as influenza and SARS-CoV-2.11 Research has demonstrated
that ML models can effectively analyze vast genomic datasets to
understand mutational patterns and predict the direction of a virus's
evolution.11 For instance, studies have employed ML to forecast
recurrent mutations in the SARS-CoV-2 genome with an area under the
curve (AUC) of 0.8.12 Specific ML algorithms such as Support Vector
Regression (SVR), Random Forest (RF), and Multi-layer Perceptron (MLP)
have been validated for this purpose, proving their effectiveness in
analyzing extensive sequence ranges and recognizing enhanced proteins.11

**3.2** **The** **Role** **of** **Deep** **Learning** **in**
**Unstructured** **Data**

The Viro-Al project correctly specifies the use of both traditional ML
libraries like Scikit-learn and deep learning frameworks such as
TensorFlow/Keras or PyTorch.1 This distinction is critical because
traditional ML algorithms, while effective for structured data (e.g.,
spreadsheets), are less suitable for the complex, unstructured data of
genomic sequences.13 Deep learning and representation learning models,
on the other hand, are designed to learn relevant features directly from
large quantities of unstructured data, a trend that is profoundly
impacting biomedical research.13 The success of deep learning methods
for genomics has been demonstrated by models like DeepVirFinder, which
uses convolutional neural networks (ConvNets) to "automatically learn
viral genomic signatures" from DNA sequences, outperforming traditional
methods in virus recognition.15 This demonstrates that the Viro-Al
system's reliance on deep learning for sequential data analysis is a
necessary and technically advanced decision for achieving its predictive
accuracy goals.1

**4.** **The** **Antidote** **Generation** **Module:** **From**
**Virtual** **Screening** **to** **Optimized** **Leads**

The Viro-Al system's Antidote Generation Module is designed to screen a
library of pharmaceutical compounds and propose new antidote formulas
with a minimum accuracy of over 70%.1 The module leverages molecular
docking algorithms, such as AutoDock or Vina, to screen potential
antidote candidates against a 3D viral protein structure using binding
afinity models.1 While molecular docking is a fundamental component of
Computer-Aided Drug Design (CADD), its application in Viro-Al requires a
more nuanced understanding of its capabilities and limitations.

**4.1** **The** **Role** **of** **Molecular** **Docking** **in**
**Viro-Al**

Molecular docking is a well-established computational method for
predicting how a small molecule ligand will bind to a target protein.8
This process is crucial for the early stages of drug development, as it
helps identify promising lead compounds by generating potential ligand
binding poses within a target binding site.16 The Viro-Al module's use
of docking to screen a compound library and rank candidates is a valid
application of this technology.1 The approach involves two independent
stages: pose generation, which aligns the ligand within the protein's
binding cavity, and scoring, which estimates the binding afinity of the
resulting complex.17

**4.2** **A** **Critical** **Analysis:** **The** **Limitations** **of**
**Docking** **for** **Binding** **Afinity**

A key area for development lies in the module's reliance on docking for
binding afinity prediction. An opinion paper on the subject states that
docking is not the right tool for reliable binding afinity prediction,
as its scoring functions have not improved significantly in the last
10-20 years.17 This is primarily due to several simplifications inherent
to the method, including the neglect of solvent effects (water), a poor
description of hydrogen bonding, and its inability to capture the "true
dynamics" of a binding event, instead producing only a static "snapshot"
of the complex.17

To address these known limitations, a more sophisticated, hybrid
approach is required. Academic research demonstrates that machine
learning can be effectively deployed to enhance binding afinity
estimations.16 This methodology can achieve state-of-the-art results by
using a small number of simple descriptors, such as protein sequence
information and ligand properties, as input for the model.16 By
combining the speed of molecular docking for pose generation with a more
reliable ML-based scoring function for afinity prediction, the Viro-Al
system can overcome the recognized weaknesses of traditional docking
methods. This hybrid approach would lead to more accurate and reliable
predictions, strengthening the scientific rigor of the antidote
generation module.

**5.** **The** **Simulation** **Module:** **A** **Pre-Clinical**
**Validation** **Gateway**

The Simulation & Visualization Module is a critical component for
pre-clinical validation, providing a dynamic 3D visualization of a
proposed antidote docking with a viral protein.1 This capability allows
researchers to refine formulas and gain critical insights before
physical testing.1 The project’s choice of technology for this module,
while strategic, should be considered as a starting point for a more
comprehensive visualization strategy.

**5.1** **The** **Role** **of** **3D** **Visualization** **in** **Drug**
**Discovery**

Accurate 3D visualization is a cornerstone of structure-based drug
design.10 Computational techniques for modeling protein-ligand
interactions are essential for understanding how

molecules will behave.18 High-fidelity 3D modeling and simulation are
crucial for assessing the fit of a ligand within a protein's binding
pocket and for exploring the dynamic behavior of molecular systems.18
This process requires a visualization tool that can both handle the
complex structural data from the PDB and render it in a way that
provides actionable insights to researchers.

**5.2** **A** **Comparative** **Analysis** **of** **Visualization**
**Tool** **Selection**

The Viro-Al project’s specification of PyVista and Open3D is a sound
decision for building an intuitive and interactive user interface.1
PyVista is a powerful, "domain agnostic" Python library that acts as an
intuitive wrapper around the complex Visualization Toolkit (VTK), making
3D data visualization and mesh analysis accessible to novice
programmers.19 Its ability to generate compelling, publication-quality
illustrations with minimal code makes it an excellent choice for a
front-end UI.20

However, for a system aiming to perform high-fidelity pre-clinical
validation, a multi-tool visualization strategy may be required. While
PyVista is a strong general-purpose tool, more specialized software
exists for complex molecular dynamics (MD) simulations. For example,
Visual Molecular Dynamics (VMD) is a well-established program
specifically designed to view, animate, and analyze the results of MD
simulations.23 Similarly, the VTX software is optimized for real-time
visualization of "massive molecular systems and molecular dynamics
trajectories".25 The MDAnalysis Python library serves as a robust
backend for analyzing MD trajectories across multiple file formats.26

A strategic approach would be to start with PyVista for its ease of use
in building the primary visualization module, while planning for the
integration of a more specialized tool like VMD or VTX to handle the
detailed analysis of molecular dynamics as the project matures. This
allows the system to remain user-friendly while also providing the
advanced, scientifically rigorous capabilities required for a truly
comprehensive simulation platform.

**Comparative** **Analysis** **of** **Molecular** **Visualization**
**Tools** **for** **Viro-Al**

||
||
||
||

||
||
||
||
||
||

**6.** **Synthesis** **and** **Strategic** **Recommendations**

The Viro-Al project's vision to transition from a reactive to a
proactive paradigm in viral threat management is not only innovative but
is scientifically and technologically sound. The system's foundational
three-pillar data architecture, its use of modern deep learning
frameworks, and its application of molecular docking are all
well-supported by cutting-edge research in computational biology and
medicine. However, the successful execution of this vision depends on a
clear understanding of and a strategic approach to the project's most
complex technical challenges.

**6.1** **Acknowledging** **the** **Viro-Al** **Project's**
**Strengths**

The Viro-Al prototype's core architectural and technological choices are
commendable. The system's reliance on leading public databases like
GenBank and the RCSB PDB ensures access to high-quality, authoritative
data.1 The project's specification of modern AI/ML frameworks such as
TensorFlow, PyTorch, and RDKit demonstrates a clear understanding of the
tools required to achieve its stated goals.1 By embracing a proactive,
predictive approach to viral threats, the Viro-Al system is positioned
at the forefront of the intersection of artificial intelligence and
medicine, a field that is poised to fundamentally change how we combat
future pandemics.1

**6.2** **Strategic** **Recommendations** **for** **the** **Team**

Based on this comprehensive analysis, the following strategic
recommendations are provided to ensure the Viro-Al prototype's robust
and scientifically rigorous implementation:

> 1\. **Prioritize** **the** **Data** **ETL** **Pipeline:** The team
> must recognize that the most significant engineering challenge is not
> merely the 30GB data volume, but the fragmentation, heterogeneity, and
> potential bias of the source data. The primary focus should be on
> building a sophisticated and automated ETL pipeline that can clean,
> normalize, and integrate disparate datasets from various sources,
> particularly for clinical and pharmaceutical data. This will directly
> impact the accuracy and reliability of the predictive models.
>
> 2\. **Integrate** **a** **Hybrid** **Approach** **for** **Antidote**
> **Generation:** The project should not rely exclusively on traditional
> molecular docking for binding afinity prediction. The team should
> formally adopt a hybrid approach that uses docking for its proven
> ability in pose generation and integrates machine learning models to
> provide a more accurate and reliable assessment of binding afinity.
> This will overcome the known limitations of docking and lead to more
> effective and scientifically sound antidote candidates.
>
> 3\. **Implement** **a** **Multi-Tool** **Visualization** **Strategy:**
> The Viro-Al team should view its choice of PyVista as the ideal
> starting point for building a user-friendly and intuitive interface,
> but plan for the integration of more specialized tools. As the project
> matures and begins to conduct more complex molecular dynamics
> simulations, a specialized program like VMD, supported by a backend
> library like MDAnalysis, will be necessary to provide the deep,
> granular analysis and visualization capabilities required for true
> pre-clinical validation.

By meticulously addressing these critical areas, the Viro-Al team can
establish a solid foundation to achieve its revolutionary goals and
deliver a truly transformative tool in the fight against viral threats.

**Works** **cited**

> 1\. Viro Ai problem statement.pdf
>
> 2\. From Data to Drugs: The Role of Artificial Intelligence in Drug
> Discovery - Wyss Institute, accessed September 23, 2025,
>
> [<u>https://wyss.harvard.edu/news/from-data-to-drugs-the-role-of-artificial-intellige</u>](https://wyss.harvard.edu/news/from-data-to-drugs-the-role-of-artificial-intelligence-in-drug-discovery/)
> [<u>nce-in-drug-discovery/</u>](https://wyss.harvard.edu/news/from-data-to-drugs-the-role-of-artificial-intelligence-in-drug-discovery/)
>
> 3\. www.scilife.io, accessed September 23, 2025,
>
> [<u>https://www.scilife.io/blog/ai-pharma-innovation-challenges#:~:text=AI%20is%20</u>](https://www.scilife.io/blog/ai-pharma-innovation-challenges#:~:text=AI%20is%20revolutionizing%20drug%20discovery,compounds%2C%20and%20predict%20their%20properties.)
> [<u>revolutionizing%20drug%20discovery,compounds%2C%20and%20predict%20th</u>](https://www.scilife.io/blog/ai-pharma-innovation-challenges#:~:text=AI%20is%20revolutionizing%20drug%20discovery,compounds%2C%20and%20predict%20their%20properties.)
> [<u>eir%20properties.</u>](https://www.scilife.io/blog/ai-pharma-innovation-challenges#:~:text=AI%20is%20revolutionizing%20drug%20discovery,compounds%2C%20and%20predict%20their%20properties.)
>
> 4\. AI in Pharma and Life Sciences \| Deloitte US, accessed September
> 23, 2025,
> [<u>https://www.deloitte.com/us/en/Industries/life-sciences-health-care/articles/ai-in-pharma-and-life-sciences.html</u>](https://www.deloitte.com/us/en/Industries/life-sciences-health-care/articles/ai-in-pharma-and-life-sciences.html)
>
> 5\. Transforming clinical virology with AI, machine learning and deep
> learning: a comprehensive review and outlook \| Request PDF -
> ResearchGate, accessed September 23, 2025,
> [<u>https://www.researchgate.net/publication/374090560_Transforming_clinical_virol</u>](https://www.researchgate.net/publication/374090560_Transforming_clinical_virology_with_AI_machine_learning_and_deep_learning_a_comprehensive_review_and_outlook)
> [<u>ogy_with_AI_machine_learning_and_deep_learning_a_comprehensive_review_an</u>](https://www.researchgate.net/publication/374090560_Transforming_clinical_virology_with_AI_machine_learning_and_deep_learning_a_comprehensive_review_and_outlook)
> [<u>d_outlook</u>](https://www.researchgate.net/publication/374090560_Transforming_clinical_virology_with_AI_machine_learning_and_deep_learning_a_comprehensive_review_and_outlook)
>
> 6\. An AI Tool That Can Help Forecast Viral Variants \| Harvard
> Medical ..., accessed September 23, 2025,
>
> [<u>https://hms.harvard.edu/news/ai-tool-can-help-forecast-viral-outbreaks</u>](https://hms.harvard.edu/news/ai-tool-can-help-forecast-viral-outbreaks)
>
> 7\. New AI tool could help predict viral outbreaks - University of
> Oxford, accessed September 23, 2025,
>
> [<u>https://www.ox.ac.uk/news/2023-10-19-new-ai-tool-could-help-predict-viral-out</u>](https://www.ox.ac.uk/news/2023-10-19-new-ai-tool-could-help-predict-viral-outbreaks)
> [<u>breaks</u>](https://www.ox.ac.uk/news/2023-10-19-new-ai-tool-could-help-predict-viral-outbreaks)

8\. Computer-Aided Drug Design and Drug Discovery - PMC - PubMed
Central, accessed September 23, 2025,
[<u>https://pmc.ncbi.nlm.nih.gov/articles/PMC11946204/</u>](https://pmc.ncbi.nlm.nih.gov/articles/PMC11946204/)

9\. Drug Target Interaction Prediction Using Machine Learning Techniques
– A Review, accessed September 23, 2025,
[<u>https://www.ijimai.org/journal/sites/default/files/2024-05/ijimai8_6_8.pdf</u>](https://www.ijimai.org/journal/sites/default/files/2024-05/ijimai8_6_8.pdf)

10\. An Overview of Molecular Docking - Asian Journal of Pharmaceutical
Research, accessed September 23, 2025,
[<u>https://asianjpr.com/HTMLPaper.aspx?Journal=Asian%20Journal%20of%20Pharm</u>](https://asianjpr.com/HTMLPaper.aspx?Journal=Asian+Journal+of+Pharmaceutical+Research;PID%3D2024-14-3-22)
[<u>aceutical%20Research;PID=2024-14-3-22</u>](https://asianjpr.com/HTMLPaper.aspx?Journal=Asian+Journal+of+Pharmaceutical+Research;PID%3D2024-14-3-22)

11\. Predicting Natural Evolution in the RBD Region of the Spike
Glycoprotein of SARS-CoV-2 by Machine Learning - MDPI, accessed
September 23, 2025,
[<u>https://www.mdpi.com/1999-4915/16/3/477</u>](https://www.mdpi.com/1999-4915/16/3/477)

12\. Prediction of Recurrent Mutations in SARS-CoV-2 Using Artificial
Neural Networks - MDPI, accessed September 23, 2025,

> [<u>https://www.mdpi.com/1422-0067/23/23/14683</u>](https://www.mdpi.com/1422-0067/23/23/14683)

13\. Toward the novel AI tasks in infection biology \| mSphere - ASM
Journals, accessed September 23, 2025,
[<u>https://journals.asm.org/doi/10.1128/msphere.00591-23</u>](https://journals.asm.org/doi/10.1128/msphere.00591-23)

14\. Deep Learning for Genomics: From Early Neural Nets to Modern Large
Language Models, accessed September 23, 2025,

> [<u>https://www.mdpi.com/1422-0067/24/21/15858</u>](https://www.mdpi.com/1422-0067/24/21/15858)

15\. Identifying viruses from metagenomic data using deep learning -
PMC, accessed September 23, 2025,
[<u>https://pmc.ncbi.nlm.nih.gov/articles/PMC8172088/</u>](https://pmc.ncbi.nlm.nih.gov/articles/PMC8172088/)

16\. Protein–ligand binding afinity prediction exploiting sequence ...,
accessed September 23, 2025,
[<u>https://academic.oup.com/bioinformatics/article/39/8/btad502/7241686</u>](https://academic.oup.com/bioinformatics/article/39/8/btad502/7241686)

17\. Binding Afinity via Docking: Fact and Fiction - MDPI, accessed
September 23, 2025,
[<u>https://www.mdpi.com/1420-3049/23/8/1899</u>](https://www.mdpi.com/1420-3049/23/8/1899)

18\. Computer Simulation of Protein-Ligand Interactions \| Springer
Nature Experiments, accessed September 23, 2025,
[<u>https://experiments.springernature.com/articles/10.1385/1-59259-912-5:451</u>](https://experiments.springernature.com/articles/10.1385/1-59259-912-5:451)

19\. Connections — PyVista 0.46.3 documentation, accessed September 23,
2025,
[<u>https://docs.pyvista.org/getting-started/connections.html</u>](https://docs.pyvista.org/getting-started/connections.html)

20\. The PyVista Project, accessed September 23, 2025,
[<u>https://pyvista.org/</u>](https://pyvista.org/)

21\. How does PyVista relate to other visualization tools? \#1438 -
GitHub, accessed September 23, 2025,
[<u>https://github.com/pyvista/pyvista/discussions/1438</u>](https://github.com/pyvista/pyvista/discussions/1438)

22\. Scientific Visualisations with Python, accessed September 23, 2025,
[<u>https://marcin.t.nowak.pracownik.put.poznan.pl/subjects/scientific-visualisations/l</u>](https://marcin.t.nowak.pracownik.put.poznan.pl/subjects/scientific-visualisations/lectures/08.html)
[<u>ectures/08.html</u>](https://marcin.t.nowak.pracownik.put.poznan.pl/subjects/scientific-visualisations/lectures/08.html)

23\. Visual Molecular Dynamics - Wikipedia, accessed September 23, 2025,
[<u>https://en.wikipedia.org/wiki/Visual_Molecular_Dynamics</u>](https://en.wikipedia.org/wiki/Visual_Molecular_Dynamics)

24\. VMD \| Visual Molecular Dynamics \| Exxact Corp, accessed September
23, 2025,
[<u>https://www.exxactcorp.com/Supported-Software/VMD</u>](https://www.exxactcorp.com/Supported-Software/VMD)

25\. VTX: Real-time high-performance molecular structure and dynamics
visualization

> software Citation - arXiv, accessed September 23, 2025,
> [<u>https://arxiv.org/html/2501.12750v1</u>](https://arxiv.org/html/2501.12750v1)

26\. MDAnalysis · MDAnalysis, accessed September 23, 2025,
[<u>https://www.mdanalysis.org/</u>](https://www.mdanalysis.org/)

27\. MDAnalysis is a Python library to analyze molecular dynamics
simulations. -GitHub, accessed September 23, 2025,
[<u>https://github.com/MDAnalysis/mdanalysis</u>](https://github.com/MDAnalysis/mdanalysis)
