import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import math
from samplerNinterpolation import sample_interpolate
from utils import get_initial_weights


def STN_Model(input_shape=(40, 40, 1), sampling_size=(40, 40), num_classes=10, reg=0.00, drop_rate=0.00, batch_norm = 0):
	# Input
	STN_Input = keras.Input(shape=input_shape, name = 'STN_Input')

	# Layers for localization network
	locnet = layers.MaxPool2D(pool_size=(2,2))(STN_Input)
	locnet = layers.Conv2D(20, (5,5), activation = 'relu', kernel_regularizer=tf.keras.regularizers.l2(reg))(locnet)
	locnet = layers.MaxPool2D(pool_size=(2, 2))(locnet)
	locnet = layers.Conv2D(20, (5,5), activation = 'relu', kernel_regularizer=tf.keras.regularizers.l2(reg))(locnet)
	locnet = layers.MaxPool2D(pool_size=(2, 2))(locnet)
	locnet = layers.Flatten()(locnet)
	locnet = layers.Dense(20, kernel_regularizer=tf.keras.regularizers.l2(reg))(locnet)
	locnet = layers.Activation('relu')(locnet)
	locnet = layers.Dropout(drop_rate)(locnet)
	weights = get_initial_weights(20)
	locnet = layers.Dense(6, weights=weights, kernel_regularizer=tf.keras.regularizers.l2(reg))(locnet)

	# Grid generator and bilenear interpolator layer
	sampler = sample_interpolate(sampling_size)([STN_Input, locnet])

	# Classification layer
	classifier = layers.Conv2D(64, (9, 9), activation = 'relu', kernel_regularizer=tf.keras.regularizers.l2(reg))(sampler)
	if batch_norm != 0:
		classifier = layers.BatchNormalization()(classifier)
	classifier = layers.MaxPool2D(pool_size=(2, 2), strides = 2)(classifier)
	classifier = layers.Conv2D(32, (7, 7), activation = 'relu', kernel_regularizer=tf.keras.regularizers.l2(reg))(classifier)
	if batch_norm != 0:
		classifier = layers.BatchNormalization()(classifier)
	classifier = layers.MaxPool2D(pool_size=(2, 2), strides = 2)(classifier)
	classifier = layers.Flatten()(classifier)
	classifier = layers.Dense(256, kernel_regularizer=tf.keras.regularizers.l2(reg))(classifier)
	classifier = layers.Activation('relu')(classifier)
	if batch_norm != 0:
		classifier = layers.BatchNormalization()(classifier)
	classifier = layers.Dropout(drop_rate)(classifier)
	classifier = layers.Dense(num_classes, kernel_regularizer=tf.keras.regularizers.l2(reg))(classifier)
	classifier_output = layers.Activation('softmax')(classifier)

	model = keras.Model(inputs=STN_Input, outputs=classifier_output)
	
	return model
