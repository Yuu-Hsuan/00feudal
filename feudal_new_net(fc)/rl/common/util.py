import numpy as np
import tensorflow as tf

from pysc2.lib.actions import TYPES as ACTION_TYPES
from pysc2.lib.actions import FunctionCall, FUNCTIONS

def compute_entropy(probs):
    return -tf.reduce_sum(safe_log(probs) * probs, axis=-1)


def flatten_first_dims(x):
    new_shape = [x.shape[0] * x.shape[1]] + list(x.shape[2:])
    return x.reshape(*new_shape)


def flatten_first_dims_dict(x):
    return {k: flatten_first_dims(v) for k, v in x.items()}


def mask_unavailable_actions(available_actions, fn_pi):
    fn_pi *= available_actions
    fn_pi += available_actions*1e-6
    #norm = tf.reduce_sum(fn_pi, axis=1, keep_dims=True)
    #if norm == 0:
    #    fn_pi = available_actions / tf.reduce_sum(available_actions, axis=1, keep_dims=True)
    #else:
    #fn_pi = safe_div(fn_pi, tf.tile(norm, [1, tf.shape(fn_pi)[1]]))
    #fn_pi /= norm

    return fn_pi


def mask_unused_argument_samples(actions):
    """Replace sampled argument id by -1 for all arguments not used
    in a steps action (in-place).
    """
    fn_id, arg_ids = actions
    for n in range(fn_id.shape[0]):
        a_0 = fn_id[n]
        unused_types = set(ACTION_TYPES) - set(FUNCTIONS._func_list[a_0].args)
        for arg_type in unused_types:
            arg_ids[arg_type][n] = -1
    return (fn_id, arg_ids)


def safe_div(numerator, denominator, name="value"):
    """Computes a safe divide which returns 0 if the denominator is zero.
    Note that the function contains an additional conditional check that is
    necessary for avoiding situations where the loss is zero causing NaNs to
    creep into the gradient computation.
    Args:
      numerator: An arbitrary `Tensor`.
      denominator: `Tensor` whose shape matches `numerator` and whose values are
        assumed to be non-negative.
      name: An optional name for the returned op.
    Returns:
      The element-wise value of the numerator divided by the denominator.
    
    return tf.where(
        tf.equal(denominator, 0)| tf.is_nan(numerator),
        tf.zeros_like(numerator),
        tf.divide(numerator,
        tf.where(tf.equal(denominator, 0), tf.ones_like(denominator), denominator)))
    """
    
    """Computes a safe divide which returns 0 if the denominator is zero.
    This function also avoids dividing by very small numbers close to zero by adding epsilon.
    """
    epsilon = 1e-6  # A small value to avoid division by very small numbers
    # Ensure that denominator is not zero or too small
    denominator = tf.where(
        tf.equal(denominator, 0) | tf.is_nan(denominator),
        tf.ones_like(denominator) * epsilon,  # Replace zero or NaN denominator with epsilon
        denominator
    )
    return tf.divide(numerator, denominator)


def safe_log(x):
    # 將 x 最低限制在 1e-6，然後取對數
    return tf.log(tf.maximum(x, 1e-6))
