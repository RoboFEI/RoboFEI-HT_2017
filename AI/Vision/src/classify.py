from defs import *

def classify(image_files, net, transformer,
             mean_file=None, labels=None, batch_size=None):
    """
    Classify some images against a Caffe model and print the results

    Arguments:
    caffemodel -- path to a .caffemodel
    deploy_file -- path to a .prototxt
    image_files -- list of paths to images

    Keyword arguments:
    mean_file -- path to a .binaryproto
    labels_file path to a .txt file
    use_gpu -- if True, run inference on the GPU
    """
#    if channels == 3:
#        mode = 'RGB'
#    elif channels == 1:
#        mode = 'L'
#    else:
#        raise ValueError('Invalid number for channels: %s' % channels)
    images = [image_files]

    # Classify the image
    scores = forward_pass(images, net, transformer, batch_size=batch_size)

    #
    # Process the results
    #
    results = {}

    indices = (-scores).argsort()[:, :7]  # take top 9 results
    classifications = []
    for image_index, index_list in enumerate(indices):
        result = []
        for i in index_list:
            # 'i' is a category in labels and also an index into scores
            if labels is None:
                label = 'Class #%s' % i
            else:
                label = labels[i]
            result.append((label, round(100.0 * scores[image_index, i], 4)))
        classifications.append(result)

    for index, classification in enumerate(classifications):
#        print '{:-^80}'.format(' Prediction for image ')
        for label, confidence in classification:
#            print '{:9.4%} - "{}"'.format(confidence / 100.0, label)
            results[label] = confidence / 100.0
#        print
    return classification[0][0], results

