import os
import time

import tensorflow as tf, sys

def initialize_session(sess, image_path):
    os.environ['TF_CPP_MIN_LOG_LEVEL']='3'
    # change this as you see fit
    # Read in the image_data
    image_data = tf.gfile.FastGFile(image_path, 'rb').read()

    # Loads label file, strips off carriage return
    label_lines = [line.rstrip() for line 
                       in tf.gfile.GFile("res/retrained_labels.txt")]

    # Unpersists graph from file
    with tf.gfile.FastGFile("res/retrained_graph.pb", 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(graph_def, name='')
    # Feed the image_data as input to the graph and get first prediction
    softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

    #run it once to get it all optmized
    predictions = sess.run(softmax_tensor, \
            {'DecodeJpeg/contents:0': image_data})

    return sess,softmax_tensor

def classify_image(sess, softmax_tensor, image_data, rejection_threshold = 0.5):
    predictions = sess.run(softmax_tensor, \
            {'DecodeJpeg/contents:0': image_data})
    # Sort to show labels of first prediction in order of confidence
    top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
    label_lines = [line.rstrip() for line 
                       in tf.gfile.GFile("res/retrained_labels.txt")]
    labels = []
    scores = []
    for i in range(5):
        labels.append(label_lines[top_k[i]])
        scores.append(predictions[0][top_k[i]])
    print(labels)
    print(scores)
    if predictions[0][top_k[0]] > rejection_threshold:
        if label_lines[top_k[0]] == 'eggs':
            if predictions[0][top[0]] < 0.75:
                return 'Error'
        return label_lines[top_k[0]]
    else:
        return "Error"
