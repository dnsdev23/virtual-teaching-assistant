# Chapter 2: Deep Learning Fundamentals

## What is Deep Learning?

Deep Learning is a subset of machine learning that uses artificial neural networks with multiple layers (deep neural networks) to model and understand complex patterns in data.

## Neural Networks

### Basic Components
- **Neurons**: Basic processing units
- **Weights**: Connection strengths between neurons
- **Biases**: Threshold values for activation
- **Activation Functions**: Determine neuron output

### Common Activation Functions
1. **ReLU (Rectified Linear Unit)**: f(x) = max(0, x)
2. **Sigmoid**: f(x) = 1 / (1 + e^(-x))
3. **Tanh**: f(x) = (e^x - e^(-x)) / (e^x + e^(-x))
4. **Softmax**: Used for multi-class classification

## Types of Neural Networks

### 1. Feedforward Neural Networks
- Information flows in one direction
- No cycles or loops
- Good for basic classification tasks

### 2. Convolutional Neural Networks (CNNs)
- Specialized for image processing
- Uses convolution operations
- Good for computer vision tasks

### 3. Recurrent Neural Networks (RNNs)
- Can process sequences of data
- Has memory capabilities
- Good for time series and NLP

### 4. Long Short-Term Memory (LSTM)
- Special type of RNN
- Solves vanishing gradient problem
- Better for long sequences

## Training Deep Networks

### Backpropagation
- Algorithm for training neural networks
- Calculates gradients using chain rule
- Updates weights to minimize loss

### Common Optimizers
- **SGD**: Stochastic Gradient Descent
- **Adam**: Adaptive Moment Estimation
- **RMSprop**: Root Mean Square Propagation

### Regularization Techniques
- **Dropout**: Randomly ignore neurons during training
- **Batch Normalization**: Normalize inputs to each layer
- **Early Stopping**: Stop training when validation loss stops improving

## Applications
1. Image Classification
2. Object Detection
3. Natural Language Processing
4. Speech Recognition
5. Game Playing (AlphaGo, Chess)
