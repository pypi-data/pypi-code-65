import matplotlib.pyplot as plt
import numpy as np
import os
import tensorflow as tf

from tensorflow.keras.preprocessing import image_dataset_from_directory

class KSModel():

    def __init__(self):
        self.BATCH_SIZE = 32
        self.IMG_SIZE = (160, 160)
        self.base_learning_rate = 0.0001
        self.epochs = 0

    def load_dataset(self, pth="dataset"):
        train_dataset = image_dataset_from_directory(pth,
                                                    shuffle=True,
                                                    batch_size=self.BATCH_SIZE,
                                                    image_size=self.IMG_SIZE,
                                                    validation_split=0.2,
                                                    subset="training",
                                                    seed=6)
        validation_dataset = image_dataset_from_directory(pth,
                                                shuffle=True,
                                                batch_size=self.BATCH_SIZE,
                                                image_size=self.IMG_SIZE,
                                                validation_split=0.2,
                                                subset="validation",
                                                seed=6)
        self.class_names = train_dataset.class_names

        val_batches = tf.data.experimental.cardinality(validation_dataset)
        test_dataset = validation_dataset.take(val_batches // 5)
        validation_dataset = validation_dataset.skip(val_batches // 5)
        print('Number of validation batches: %d' % tf.data.experimental.cardinality(validation_dataset))
        print('Number of test batches: %d' % tf.data.experimental.cardinality(test_dataset))

        AUTOTUNE = tf.data.experimental.AUTOTUNE

        self.train_dataset = train_dataset.prefetch(buffer_size=AUTOTUNE)
        self.validation_dataset = validation_dataset.prefetch(buffer_size=AUTOTUNE)
        self.test_dataset = test_dataset.prefetch(buffer_size=AUTOTUNE)

        self.preprocess_input = tf.keras.applications.mobilenet_v2.preprocess_input
        self.create_augs()
        self.create_model()

    def create_augs(self):
        self.data_augmentation = tf.keras.Sequential([
            tf.keras.layers.experimental.preprocessing.RandomFlip('horizontal'),
            tf.keras.layers.experimental.preprocessing.RandomRotation(0.2),
        ])

    def show_imgs(self):
        plt.figure(figsize=(10, 10))
        for images, labels in self.train_dataset.take(1):
            for i in range(9):
                ax = plt.subplot(3, 3, i + 1)
                plt.imshow(images[i].numpy().astype("uint8"))
                plt.title(self.class_names[labels[i]])
                plt.axis("off")

    def create_model(self):
        # Create the base model from the pre-trained model MobileNet V2
        IMG_SHAPE = self.IMG_SIZE + (3,)
        self.base_model = tf.keras.applications.MobileNetV2(input_shape=IMG_SHAPE,
                                                    include_top=False,
                                                    weights='imagenet')

        # freeze base
        self.base_model.trainable = False

        #
        image_batch, label_batch = next(iter(self.train_dataset))
        feature_batch = self.base_model(image_batch)

        # add classification head
        global_average_layer = tf.keras.layers.GlobalAveragePooling2D()
        feature_batch_average = global_average_layer(feature_batch)
        prediction_layer = tf.keras.layers.Dense(1)
        prediction_batch = prediction_layer(feature_batch_average)

        # Build a model by chaining together the data augmentation, rescaling, base_model and feature extractor layers
        inputs = tf.keras.Input(shape=(160, 160, 3))
        x = self.data_augmentation(inputs)
        x = self.preprocess_input(x)
        x = self.base_model(x, training=False)
        x = global_average_layer(x)
        x = tf.keras.layers.Dropout(0.2)(x)
        outputs = prediction_layer(x)
        self.model = tf.keras.Model(inputs, outputs)

        # compile the model
        self.model.compile(optimizer=tf.keras.optimizers.Adam(lr=self.base_learning_rate),
                loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
                metrics=['accuracy'])

    def train(self, nb_epochs):
        self.epochs += nb_epochs
        loss0, accuracy0 = self.model.evaluate(self.validation_dataset)
        print("initial loss: {:.2f}".format(loss0))
        print("initial accuracy: {:.2f}".format(accuracy0))

        self.history = self.model.fit(self.train_dataset,
                        epochs=self.epochs,
                        validation_data=self.validation_dataset)

    def fine_tune(self, nb_epochs):
        # un-freeze base layers
        self.base_model.trainable = True

        # Let's take a look to see how many layers are in the base model
        print("Number of layers in the base model: ", len(self.base_model.layers))

        # Fine-tune from this layer onwards
        fine_tune_at = 100

        # Freeze all the layers before the `fine_tune_at` layer
        for layer in self.base_model.layers[:fine_tune_at]:
            layer.trainable =  False

        self.model.compile(loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
                optimizer = tf.keras.optimizers.RMSprop(lr=self.base_learning_rate/10),
                metrics=['accuracy'])

        self.epochs += nb_epochs

        self.history_fine = self.model.fit(self.train_dataset,
                            epochs=self.epochs,
                            initial_epoch=self.history.epoch[-1],
                            validation_data=self.validation_dataset)

    def display_metrics(self, history):
        acc = history.history['accuracy']
        val_acc = history.history['val_accuracy']

        loss = history.history['loss']
        val_loss = history.history['val_loss']

        plt.figure(figsize=(8, 8))
        plt.subplot(2, 1, 1)
        plt.plot(acc, label='Training Accuracy')
        plt.plot(val_acc, label='Validation Accuracy')
        plt.legend(loc='lower right')
        plt.ylabel('Accuracy')
        plt.ylim([min(plt.ylim()),1])
        plt.title('Training and Validation Accuracy')

        plt.subplot(2, 1, 2)
        plt.plot(loss, label='Training Loss')
        plt.plot(val_loss, label='Validation Loss')
        plt.legend(loc='upper right')
        plt.ylabel('Cross Entropy')
        plt.ylim([0,1.0])
        plt.title('Training and Validation Loss')
        plt.xlabel('epoch')
        plt.show()