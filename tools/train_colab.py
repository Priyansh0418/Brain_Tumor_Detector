"""
Colab-ready training script for Brain Tumor Detector

Usage in Colab:
1. Upload your dataset ZIP (or use Kaggle API) and extract to /content/data
2. Run this script in a Colab cell: 
   !python /content/Brain_Tumor_Detector/tools/train_colab.py --data_dir /content/data --output /content/bt_model.h5

Notes:
- The script uses TensorFlow and EfficientNetB0 for transfer learning.
- It saves the best model to the specified output path.
- Designed for binary classification: Tumor vs Normal. Expect folder structure:
    /path/to/data/
      train/
        tumor/
        normal/
      val/
        tumor/
        normal/

If you have a multi-class dataset, you can adapt --classes parameter accordingly.

This script is intentionally simple and works well in Colab with the default GPU runtime.
"""

import argparse
import os
import math
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Optional sklearn for evaluation (confusion matrix / classification report)
try:
    from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score
    from sklearn.utils.class_weight import compute_class_weight
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False


def build_model(input_shape=(224,224,3), base_trainable=False):
    base = EfficientNetB0(include_top=False, weights='imagenet', input_shape=input_shape)
    base.trainable = base_trainable
    inputs = layers.Input(shape=input_shape)
    x = base(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(1, activation='sigmoid')(x)
    model = models.Model(inputs, outputs)
    return model


def get_generators(data_dir, target_size=(224,224), batch_size=16):
    # Basic augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=10,
        width_shift_range=0.05,
        height_shift_range=0.05,
        shear_range=0.05,
        zoom_range=0.05,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    val_datagen = ImageDataGenerator(rescale=1./255)

    train_gen = train_datagen.flow_from_directory(
        os.path.join(data_dir, 'train'),
        target_size=target_size,
        batch_size=batch_size,
        class_mode='binary'
    )
    val_gen = val_datagen.flow_from_directory(
        os.path.join(data_dir, 'val'),
        target_size=target_size,
        batch_size=batch_size,
        class_mode='binary'
    )
    return train_gen, val_gen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, required=True, help='Path to dataset root (train/val subfolders)')
    parser.add_argument('--output', type=str, default='bt_model.h5', help='Output model path')
    parser.add_argument('--saved_model_dir', type=str, default=None, help='Optional path to save TensorFlow SavedModel folder')
    parser.add_argument('--epochs', type=int, default=12)
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--lr', type=float, default=1e-4)
    parser.add_argument('--image_size', type=int, default=224, help='Spatial size (square) to resize images to')
    parser.add_argument('--use_class_weights', action='store_true', help='Automatically compute and use class weights from training set')
    parser.add_argument('--tensorboard_logdir', type=str, default=None, help='Optional TensorBoard log dir')
    args = parser.parse_args()

    print('TensorFlow version:', tf.__version__)

    target = (args.image_size, args.image_size)
    train_gen, val_gen = get_generators(args.data_dir, target_size=target, batch_size=args.batch_size)

    model = build_model((args.image_size, args.image_size, 3), base_trainable=False)
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=args.lr), loss='binary_crossentropy', metrics=['accuracy'])

    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(args.output, monitor='val_loss', save_best_only=True, verbose=1),
        tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=4, restore_best_weights=True)
    ]
    if args.tensorboard_logdir:
        callbacks.append(tf.keras.callbacks.TensorBoard(log_dir=args.tensorboard_logdir))

    # Optionally compute class weights
    class_weight = None
    if args.use_class_weights:
        try:
            # infer classes from train_gen.class_indices
            classes = list(train_gen.class_indices.keys())
            # build list of labels for all training samples
            labels = train_gen.classes
            if SKLEARN_AVAILABLE:
                cw = compute_class_weight(class_weight='balanced', classes=np.unique(labels), y=labels)
                class_weight = {i: float(w) for i, w in enumerate(cw)}
                print('Using class weights:', class_weight)
            else:
                # simple heuristic: inverse frequency
                vals, counts = np.unique(labels, return_counts=True)
                inv = {int(v): float(max(counts) / c) for v, c in zip(vals, counts)}
                class_weight = inv
                print('Using heuristic class weights (sklearn not installed):', class_weight)
        except Exception as e:
            print('Could not compute class weights, proceeding without them:', e)

    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=args.epochs,
        callbacks=callbacks,
        class_weight=class_weight
    )

    print('Training finished. Best model saved to', args.output)

    # Save SavedModel dir if requested
    if args.saved_model_dir:
        try:
            model.save(args.saved_model_dir, save_format='tf')
            print('SavedModel exported to', args.saved_model_dir)
        except Exception as e:
            print('Failed to save SavedModel:', e)

    # Evaluation on validation set
    try:
        print('Running evaluation on validation set...')
        # collect all validation images and labels
        val_steps = int(math.ceil(val_gen.samples / val_gen.batch_size))
        preds = model.predict(val_gen, steps=val_steps)
        # preds shape: (N,1)
        probs = np.asarray(preds).reshape(-1)
        y_true = val_gen.classes[: len(probs)]

        if SKLEARN_AVAILABLE:
            y_pred = (probs >= 0.5).astype(int)
            print('\nClassification report:')
            print(classification_report(y_true, y_pred, target_names=list(val_gen.class_indices.keys())))
            try:
                auc = roc_auc_score(y_true, probs)
                print('ROC AUC:', auc)
            except Exception:
                pass
            print('Confusion matrix:')
            print(confusion_matrix(y_true, y_pred))
        else:
            acc = np.mean((probs >= 0.5).astype(int) == val_gen.classes[: len(probs)])
            print(f'Validation accuracy (approx): {acc:.4f}')
    except Exception as e:
        print('Evaluation failed:', e)


if __name__ == '__main__':
    main()
