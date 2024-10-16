# -*- coding: utf-8 -*-


import tensorflow as tf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
df = pd.read_csv('Admission_Predict_A3.csv')
from tensorflow.keras.optimizers.legacy import SGD

print(df.columns)

df.head()
df.isnull().sum()

## Splitting the Dataset
df_train, df_test = train_test_split(df,test_size=0.30, random_state=42)

from sklearn.preprocessing import StandardScaler

X=df.drop('Chance of Admit ', axis=1)
y=df['Chance of Admit ']
scaler = StandardScaler()
X_scaled=scaler.fit_transform(X)

X_train_tensor = tf.constant(X_scaled, dtype = tf.float32)
y_train_tensor = tf.constant(y.values.reshape(-1,1),
dtype=tf.float32)   #Reshape to 400,1

num_features = X_scaled.shape[1]
weights = tf.Variable(tf.random.normal(shape=(num_features, 1)), dtype=tf.float32)
bias = tf.Variable(tf.zeros(shape=(1,)), dtype=tf.float32)


def linear_regression(X):
    return tf.matmul(X, weights) + bias


def mean_squared_error(y_true, y_pred):
    return tf.reduce_mean(tf.square(y_true - y_pred))


y_pred = linear_regression(X_train_tensor)


loss = mean_squared_error(y_train_tensor, y_pred)


print("Initial Loss:", loss.numpy())

learning_rate = 0.01
optimizer = tf.optimizers.legacy.SGD(learning_rate)


epochs = 1000

for epoch in range(epochs):
    with tf.GradientTape() as tape:

        y_pred = linear_regression(X_train_tensor)
        loss = mean_squared_error(y_train_tensor, y_pred)


    gradients = tape.gradient(loss, [weights, bias])


    optimizer.apply_gradients(zip(gradients, [weights, bias]))


    if (epoch + 1) % 20 == 0:
        print(f"Epoch {epoch + 1}/{epochs}, Loss: {loss.numpy()}")


print("Final Weights:", weights.numpy())
print("Final Bias:", bias.numpy())

num_features_test = X_test_scaled.shape[1]


weights_test = tf.Variable(tf.random.normal(shape=(num_features_test, 1)), dtype=tf.float32)


bias_test = tf.Variable(tf.zeros(shape=(1,)), dtype=tf.float32)


def linear_regression_test(X):
    return tf.matmul(X, weights_test) + bias_test


y_test_pred = linear_regression_test(X_test_tensor)


test_loss = mean_squared_error(y_test_tensor, y_test_pred)
print(f"Test Mean Squared Error (MSE): {float(test_loss)}")

plt.scatter(y_test_tensor, y_test_pred, alpha=0.5)
plt.title('Actual vs Predicted Probabilities')
plt.xlabel('Actual Probabilities')
plt.ylabel('Predicted Probabilities')
plt.show()

bin_edges_logistic = [0, 0.5, 0.75, 1.0]
bin_labels_logistic = ['Low', 'Medium', 'High']
df_train['Admit_Category'] = pd.cut(df_train['Chance of Admit '], bins=bin_edges_logistic, labels=bin_labels_logistic)
df_test['Admit_Category'] = pd.cut(df_test['Chance of Admit '], bins=bin_edges_logistic, labels=bin_labels_logistic)


X_bin_train_logistic = df_train.drop(['Chance of Admit ', 'Admit_Category'], axis=1)
y_bin_train_logistic = pd.Categorical(df_train['Admit_Category']).codes

X_bin_test_logistic = df_test.drop(['Chance of Admit ', 'Admit_Category'], axis=1)
y_bin_test_logistic = pd.Categorical(df_test['Admit_Category']).codes


scaler_bin_logistic = StandardScaler()
X_bin_train_scaled_logistic = scaler_bin_logistic.fit_transform(X_bin_train_logistic)
X_bin_test_scaled_logistic = scaler_bin_logistic.transform(X_bin_test_logistic)


X_bin_train_tensor_logistic = tf.constant(X_bin_train_scaled_logistic, dtype=tf.float32)
y_bin_train_tensor_logistic = tf.constant(y_bin_train_logistic, dtype=tf.float32)
X_bin_test_tensor_logistic = tf.constant(X_bin_test_scaled_logistic, dtype=tf.float32)
y_bin_test_tensor_logistic = tf.constant(y_bin_test_logistic, dtype=tf.float32)


logistic_model = tf.keras.Sequential([
    tf.keras.layers.Dense(1, activation='sigmoid')
])


logistic_model.compile(optimizer='sgd', loss='binary_crossentropy', metrics=['accuracy'])


logistic_epochs = 50
logistic_losses = []

for epoch in range(logistic_epochs):
    with tf.GradientTape() as tape:
        y_pred_bin_logistic = logistic_model(X_bin_train_tensor_logistic)
        # Ensure the shapes are consistent for binary cross-entropy
        y_bin_train_tensor_logistic_reshaped = tf.reshape(y_bin_train_tensor_logistic, (-1, 1))
        y_pred_bin_logistic_reshaped = tf.reshape(y_pred_bin_logistic, (-1, 1))

        loss_logistic = tf.reduce_mean(tf.keras.losses.binary_crossentropy(y_bin_train_tensor_logistic_reshaped, y_pred_bin_logistic_reshaped))

    gradients_logistic = tape.gradient(loss_logistic, logistic_model.trainable_variables)
    optimizer.apply_gradients(zip(gradients_logistic, logistic_model.trainable_variables))
    logistic_losses.append(loss_logistic.numpy())

    if (epoch + 1) % 10 == 0:
        print(f"Logistic Epoch {epoch + 1}/{logistic_epochs}, Loss: {loss_logistic.numpy()}")

num_classes = len(bin_labels_logistic)

multiclass_model = tf.keras.Sequential([
    tf.keras.layers.Dense(num_classes, activation='softmax')
])


multiclass_model.compile(optimizer='sgd', loss='sparse_categorical_crossentropy', metrics=['accuracy'])


multiclass_epochs = 50
multiclass_losses = []

for epoch in range(multiclass_epochs):
    with tf.GradientTape() as tape:
        y_pred_multiclass = multiclass_model(X_bin_train_tensor_logistic)

        loss_multiclass = tf.reduce_mean(tf.keras.losses.sparse_categorical_crossentropy(y_bin_train_tensor_logistic, y_pred_multiclass))

    gradients_multiclass = tape.gradient(loss_multiclass, multiclass_model.trainable_variables)
    optimizer.apply_gradients(zip(gradients_multiclass, multiclass_model.trainable_variables))
    multiclass_losses.append(loss_multiclass.numpy())

    if (epoch + 1) % 10 == 0:
        print(f"Multiclass Epoch {epoch + 1}/{multiclass_epochs}, Loss: {loss_multiclass.numpy()}")

def train_linear_regression(X_train, y_train, learning_rate):
    num_features = X_train.shape[1]
    weights = tf.Variable(tf.random.normal(shape=(num_features, 1)), dtype=tf.float32)
    bias = tf.Variable(tf.zeros(shape=(1,)), dtype=tf.float32)

    optimizer = tf.optimizers.SGD(learning_rate)

    for epoch in range(100):
        with tf.GradientTape() as tape:
            y_pred = tf.matmul(X_train, weights) + bias
            loss = mean_squared_error(y_train, y_pred)

        gradients = tape.gradient(loss, [weights, bias])
        optimizer.apply_gradients(zip(gradients, [weights, bias]))

    return weights, bias


X_train_lr = tf.cast(X_train_lr, dtype=tf.float32)
y_train_lr = tf.cast(y_train_lr, dtype=tf.float32)
X_test_lr = tf.cast(X_test_lr, dtype=tf.float32)


X_train_tensor_lr = tf.expand_dims(X_train_lr, axis=-1)


learning_rates = [0.1, 0.01, 0.001]

for lr in learning_rates:
    weights, bias = train_linear_regression(X_train_tensor_lr, y_train_lr, lr)


    X_test_tensor_lr = tf.expand_dims(X_test_lr, axis=-1)
    y_test_pred_lr = tf.matmul(X_test_tensor_lr, weights) + bias


    test_loss_lr = mean_squared_error(y_test_lr, y_test_pred_lr)

    print(f"Test Mean Squared Error (MSE) with Learning Rate {lr}: {test_loss_lr.numpy()}")


    plt.scatter(X_test_lr, y_test_lr, label='Actual', alpha=0.5)
    plt.scatter(X_test_lr, y_test_pred_lr, label='Predicted', alpha=0.5)
    plt.title(f'Actual vs Predicted Values (Learning Rate {lr})')
    plt.xlabel('Feature')
    plt.ylabel('Target')
    plt.legend()
    plt.show()

correlation_matrix = df.corr()
correlation_with_target = correlation_matrix['Chance of Admit '].sort_values(ascending=False)


plt.figure(figsize=(10, 6))
correlation_with_target.drop('Chance of Admit ').plot(kind='bar', color='skyblue')
plt.title('Correlation Coefficients with Target Variable')
plt.xlabel('Features')
plt.ylabel('Correlation Coefficient')
plt.show()

top_features = correlation_with_target.index[1:6]


X_selected = df[top_features]
y_selected = df['Chance of Admit ']


X_train_selected, X_test_selected, y_train_selected, y_tesz t_selected = train_test_split(X_selected, y_selected, test_size=0.30, random_state=42)


scaler_selected = StandardScaler()
X_train_selected_scaled = scaler_selected.fit_transform(X_train_selected)
X_test_selected_scaled = scaler_selected.transform(X_test_selected)


X_train_selected_tensor = tf.constant(X_train_selected_scaled, dtype=tf.float32)
y_train_selected_tensor = tf.constant(y_train_selected.values.reshape(-1, 1), dtype=tf.float32)
X_test_selected_tensor = tf.constant(X_test_selected_scaled, dtype=tf.float32)
y_test_selected_tensor = tf.constant(y_test_selected.values.reshape(-1, 1), dtype=tf.float32)


weights_selected, bias_selected = train_linear_regression(X_train_selected_tensor, y_train_selected_tensor, learning_rate=0.01)


y_test_pred_selected = tf.matmul(X_test_selected_tensor, weights_selected) + bias_selected


test_loss_selected = mean_squared_error(y_test_selected_tensor, y_test_pred_selected)
print(f"Test Mean Squared Error (MSE) with Feature Selection: {test_loss_selected.numpy()}")


plt.scatter(y_test_selected, y_test_pred_selected, alpha=0.5)
plt.title('Actual vs Predicted Probabilities (Feature Selection)')
plt.xlabel('Actual Probabilities')
plt.ylabel('Predicted Probabilities')
plt.show()

from sklearn.model_selection import cross_val_score, KFold
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_squared_error, accuracy_score


linear_regression_model = LinearRegression()


kf = KFold(n_splits=5, shuffle=True, random_state=42)
linear_regression_mse_cv = -cross_val_score(linear_regression_model, X_scaled, y, cv=kf, scoring='neg_mean_squared_error').mean()

print(f"Linear Regression Mean Squared Error (MSE) with Cross-Validation: {linear_regression_mse_cv}")


logistic_regression_model = LogisticRegression(max_iter=10000)


kf = KFold(n_splits=5, shuffle=True, random_state=42)
logistic_regression_accuracy_cv = cross_val_score(logistic_regression_model,X_bin_train_logistic, y_bin_train_logistic, cv=kf, scoring='accuracy').mean()

print(f"Logistic Regression Accuracy with Cross-Validation: {logistic_regression_accuracy_cv}")

X_train_logistic, X_test_logistic, y_train_logistic, y_test_logistic = train_test_split(X_bin_train_logistic, y_bin_train_logistic, test_size=0.3, random_state=42)


X_train_tensor_logistic = tf.constant(X_train_logistic, dtype=tf.float32)
y_train_tensor_logistic = tf.constant(y_train_logistic, dtype=tf.float32)
X_test_tensor_logistic = tf.constant(X_test_logistic, dtype=tf.float32)
y_test_tensor_logistic = tf.constant(y_test_logistic, dtype=tf.float32)



logistic_model = tf.keras.Sequential([
    tf.keras.layers.Dense(1, activation='sigmoid')
])


logistic_model.compile(optimizer='sgd', loss='binary_crossentropy', metrics=['accuracy'])

logistic_epochs = 50
logistic_losses = []

for epoch in range(logistic_epochs):
    with tf.GradientTape() as tape:
        y_pred_logistic = logistic_model(X_train_tensor_logistic)
        loss_logistic = tf.reduce_mean(tf.keras.losses.binary_crossentropy(y_train_tensor_logistic, tf.reshape(y_pred_logistic, [-1])))

    gradients_logistic = tape.gradient(loss_logistic, logistic_model.trainable_variables)
    optimizer.apply_gradients(zip(gradients_logistic, logistic_model.trainable_variables))
    logistic_losses.append(loss_logistic.numpy())

    if (epoch + 1) % 10 == 0:
        print(f"Logistic Epoch {epoch + 1}/{logistic_epochs}, Loss: {loss_logistic.numpy()}")


y_pred_bin_logistic = np.round(logistic_model.predict(X_test_tensor_logistic))


logistic_test_accuracy = accuracy_score(y_test_logistic, np.squeeze(y_pred_bin_logistic))
print(f"Logistic Regression Test Accuracy: {logistic_test_accuracy}")
