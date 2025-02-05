"""
Train DenseNet201 model.
"""
from keras.applications import DenseNet201
from keras.applications.densenet import preprocess_input
from keras.models import load_model

from chess_piece_models_common import (
    build_model,
    data_generators,
    train_model,
    plot_model_history,
    evaluate_model,
    model_callbacks,
)


def train_chesspiece_model():
    """Trains the chesspiece model based on DenseNet201."""
    base_model = DenseNet201(
        input_shape=(224, 224, 3), include_top=False, weights="imagenet"
    )

    # First train only the top layers
    for layer in base_model.layers:
        layer.trainable = False

    model = build_model(base_model)

    train_generator, validation_generator = data_generators(
        preprocess_input, (224, 224), 64
    )

    callbacks = model_callbacks(5, "./models/DenseNet201_pre.h5", 0.1, 10)

    history = train_model(
        model,
        20,
        train_generator,
        validation_generator,
        callbacks,
        use_weights=False,
        workers=5,
    )

    plot_model_history(
        history, "./models/DenseNet201_pre_acc.png", "./models/DenseNet201_pre_loss.png"
    )
    evaluate_model(model, validation_generator)

    # Also train conv5
    for layer in model.layers[:481]:
        layer.trainable = False
    for layer in model.layers[481:]:
        layer.trainable = True

    model.compile(
        optimizer="Adam", loss="categorical_crossentropy", metrics=["accuracy"]
    )

    callbacks = model_callbacks(20, "./models/DenseNet201.h5", 0.2, 8)

    history = train_model(
        model,
        100,
        train_generator,
        validation_generator,
        callbacks,
        use_weights=False,
        workers=5,
    )

    plot_model_history(
        history, "./models/DenseNet201_acc.png", "./models/DenseNet201_loss.png"
    )
    evaluate_model(model, validation_generator)

    model.save("./models/DenseNet201_last.h5")


def continue_training():
    """Continues training the chesspiece model based on DenseNet201."""
    model = load_model("./models/DenseNet201.h5")

    train_generator, validation_generator = data_generators(
        preprocess_input, (224, 224), 64
    )

    # Train all layers
    for layer in model.layers:
        layer.trainable = True

    model.compile(
        optimizer="Adam", loss="categorical_crossentropy", metrics=["accuracy"]
    )

    callbacks = model_callbacks(20, "./models/DenseNet201_all.h5", 0.2, 8)

    history = train_model(
        model,
        100,
        train_generator,
        validation_generator,
        callbacks,
        use_weights=False,
        workers=5,
    )

    plot_model_history(
        history, "./models/DenseNet201_all_acc.png", "./models/DenseNet201_all_loss.png"
    )
    evaluate_model(model, validation_generator)

    model.save("./models/DenseNet201_all_last.h5")


if __name__ == "__main__":
    train_chesspiece_model()
    continue_training()
