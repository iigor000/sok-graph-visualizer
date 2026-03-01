from rdflib.term import Literal
from rdflib.namespace import XSD
from datetime import date


def convert_literal(literal: Literal):

    if literal.datatype == XSD.integer:
        return int(literal)

    elif literal.datatype == XSD.float:
        return float(literal)

    elif literal.datatype == XSD.double:
        return float(literal)

    elif literal.datatype == XSD.date:
        return date.fromisoformat(str(literal))

    else:
        return str(literal)  