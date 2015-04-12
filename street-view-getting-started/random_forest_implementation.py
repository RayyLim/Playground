import cv2
import os
from pandas import DataFrame, Series
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


def read_image(filename):
    image = cv2.imread(filename, cv2.CV_LOAD_IMAGE_GRAYSCALE)
    return image.ravel()


def generate_idx(filename):
    return int(filename.strip('.Bmp'))


def generate_features(image_dir):
    filenames = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]
    filepaths = [os.path.join(image_dir, f) for f in filenames]
    indexes = map(generate_idx, filenames)
    return DataFrame(map(read_image, filepaths), index=indexes)


def generate_labels(train_labels_filepath):
    return pd.read_csv(train_labels_filepath)


if __name__ == "__main__":
    train_dir = '/Users/ray/Downloads/trainResized'
    test_dir = '/Users/ray/Downloads/testResized'
    train_labels_filepath = '/Users/ray/Downloads/trainLabels.csv'

    # download the features per image (train)
    train_features = generate_features(train_dir)

    # download the labels
    train_labels = generate_labels(train_labels_filepath)

    # merge the features with labels
    train_data = pd.merge(left=train_labels, right=train_features, left_on='ID', right_index=True)

    # train the model
    forest_classifier = RandomForestClassifier(n_estimators=100)
    training_input = train_data.ix[:, 2:].values
    target_values = train_data['Class'].apply(lambda x: ord(x)).values
    forest_model = forest_classifier.fit(training_input, target_values)

    # download the features per image (test)
    test_features = generate_features(test_dir)

    # predict the test
    test_labels_raw = forest_model.predict(test_features)
    test_labels = Series(test_labels_raw, index=test_features.index).apply(lambda x: chr(x))

    # build output for the test
    test_labels.name = 'Class'
    test_labels.to_csv('/Users/ray/Downloads/result.csv', index_label='Id', header=True)