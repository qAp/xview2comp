
# xview2comp

> Work done for the [xView2](https://xview2.org/) competition (2019), a computer vision competition to identify buildings and give a score for the amount of damage due to a natural disaster event.

The content of this repository is briefly summarised in this blog post: [Assessing Natural Disaster Damage](https://personal-record.onrender.com/post/xview2comp/).  The code is based on Fastai.  In particular, notebooks 01 to 02 use the version used in the Fastai Part2 2019 course.  However, this workflow is incomplete.  From notebook 02b onwards, the official Fastai v1 is used.  This workflow is complete.  

Outline of notebooks:

- [*01_load_data.ipynb*](https://github.com/qAp/xview2comp/blob/master/nbs/01_load_data.ipynb)   
  Build data processing pipeline for building segmentation with `geopandas`, `cv2`, `shapely`, `PIL`, and no `torch`.  This includes:  
  - Converting polygons from well-known text (wkt) to masks.
  - Converting polygons from masks to well-known text (wkt).
  - Converting images to tensors/arrays.
  - Resizing images.
  - Normalising images.
  - Labelling images with masks.
  The result is that each pre-disaster image has a corresponding png file containing a binary mask indicating where there is a building.
  
- [*01b_load_data_2in1out.ipynb*](https://github.com/qAp/xview2comp/blob/master/nbs/01b_load_data_2in1out.ipynb)  
  Build data processing pipeline to serve data where the training input are the pre-disaster and post-disaster images, and the output is a multi-category mask indicating both where the buildings are and what their damage level is.
  
- [*01c_tier3_bmasks.ipynb*](https://github.com/qAp/xview2comp/blob/master/nbs/01c_tier3_bmasks.ipynb)  
  Generate binary masks for the Tier3 dataset.
  
- [*02_model.ipynb*](https://github.com/qAp/xview2comp/blob/master/nbs/02_model.ipynb)  
  Define loss function and metrics and set up fastai's `DynamicUnet` for building segmentation training, with callbacks for monitoring and recording training progress.
  
- [*02b_building_detection.ipynb*](https://github.com/qAp/xview2comp/blob/master/nbs/02b_building_detection.ipynb)  
  Building segmentation training, but with fastai1 instead.
  
- [*02c_bmask_to_polygons.ipynb*](https://github.com/qAp/xview2comp/blob/master/nbs/02c_bmask_to_polygons.ipynb)  
  Convert output segmentation masks to polygons and crop out the underlying post-disaster images.  Create dataset for damage classification training.
  
- [*02d_tier3_classification_samples.ipynb*](https://github.com/qAp/xview2comp/blob/master/nbs/02d_tier3_classification_samples.ipynb)  
  Create damage classification dataset from the Tier3 dataset.
  
- [*03_damage_classification.ipynb*](https://github.com/qAp/xview2comp/blob/master/nbs/03_damage_classification.ipynb)  
  Damage classification training.  Train Resnets to classify the damage level of individual building image crops.
  
- [*03b_inference_pipeline.ipynb*](https://github.com/qAp/xview2comp/blob/master/nbs/03b_inference_pipeline.ipynb)  
  Build end-to-end inference pipeline based on the trained segmentation model and the trained damage classification model, outputting png files containing masks that show where the buildings are and what their damage level is, ready for submission to the competition.


