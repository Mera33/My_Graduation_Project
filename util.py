from flask import redirect, session
from functools import wraps
from keras import models
import re
import numpy as np


def login_required(f):
    """
    A flag that the route requires login to access
    Automatically redirects the user to the login page
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def convert_email(email):
    """
    Removes Invalid Characters from an email and returns a Valid String that will be stored on firebase
    """
    return re.sub(r"[^a-zA-Z0-9 ]", "", email)


def predict(sequence):
    """
    Takes a sequence and returns the predicted category of the sequence
    """
    # Checking that the sequence is valid
    for c in sequence:
        if c not in "ATGC":
            return None
    

    seq_matrix=np.zeros((4,len(sequence)))
    j=0
    for char in sequence:
        if char == 'A':
            seq_matrix[0][j]=1
        if char == 'T':
            seq_matrix[1][j]=1
        if char == 'C':
            seq_matrix[2][j]=1
        if char == 'G':
            seq_matrix[3][j]=1
        j+=1

    ss = seq_matrix.flatten()
    ss = np.reshape(ss, (-1, 2048, 1))
    cats = ['HSC: hematopoietic stem cell', 'GMP-C: Granulocyte-Monocyte progenitor -C cell', 'LMPP: lymphoid-primed multipotent progenitors cell',
            'MEP: megakaryocyte-erythroid progenitor cell', 'GMP-B: granulocyte-macrophage progenitor-B cell', 'GMP-A: Granulocyte-Monocyte Progenitor - A cell', 
            'CMP: common myeloid progenitor cell', 'pDC: plasmacytoid dendritic cell', 'MPP: multipotent progenitor cell']
    model = models.load_model("model.h5")
    return cats[model.predict(ss).argmax()]
