#!/usr/bin/env python3
"""
Validate JSON payload with WebRotas schemas.

This module extends the JSON schema validation to apply defaults for missing fields.
"""

import jsonschema
from jsonschema import validators
import logging

# ----------------------------------------------------------------------------------------------
# Define schemas with defaults for each request type
SCHEMAS = {
    "PontosVisita": {
        "type": "object",
        "required": ["ssid", "TipoRequisicao", "PontoInicial" , "pontosvisita"],
        "properties": {
            "User": {"type": "string"},
            "TipoRequisicao": {"type": "string"},
            "PontoInicial": {
                "type": "array",
                "minItems": 3
            },
            "RaioDaEstacao": {"type": "number", "default": 200},
            "GpsProximoPonto": {"type": "string", "default": "ProximoDaRota"},
            "pontosvisita": {"type": "array", "minItems": 1},
            "AlgoritmoOrdenacaoPontos": {"type": "string", "default": "DistanciaGeodesica"},
            "regioes": {"type": "array", "default": []}
        }
    },
    "Abrangencia": {
        "type": "object", 
        "required": ["ssid", "TipoRequisicao",  "PontoInicial", "cidade", "uf", "distancia_pontos"],
        "properties": {
            "User": {"type": "string"},
            "TipoRequisicao": {"type": "string"},
            "PontoInicial": {
                "type": "array",
                "minItems": 3
            },
            "RaioDaEstacao": {"type": "number", "default": 200},
            "GpsProximoPonto": {"type": "string", "default": "ProximoDaRota"},
            "cidade": {"type": "string"},
            "uf": {"type": "string"},
            "AlgoritmoOrdenacaoPontos": {"type": "string", "default": "DistanciaGeodesica"},
            "distancia_pontos": {"type": "number"},
            "regioes": {"type": "array", "default": []}
        }
    },
    "Contorno": {
        "type": "object",
        "required": ["ssid", "TipoRequisicao", "PontoInicial", "latitude", "longitude", "raio"],
        "properties": {
            "User": {"type": "string"},
            "TipoRequisicao": {"type": "string"},
            "PontoInicial": {
                "type": "array",
                "minItems": 3
            },
            "RaioDaEstacao": {"type": "number", "default": 200},
            "GpsProximoPonto": {"type": "string", "default": "ProximoDaRota"},
            "latitude": {"type": "number"},
            "longitude": {"type": "number"},
            "raio": {"type": "number"},
            "numeropontos": {"type": "integer", "default": 20},
            "AlgoritmoOrdenacaoPontos": {"type": "string", "default": "DistanciaGeodesica"},
            "regioes": {"type": "array", "default": []}
        }
    },
    "StandardCache": {
        "type": "object",
        "properties": {
            "TipoRequisicao": {
                "type": "string",
                "enum": ["StandardCache"]
            },
            "RegioesCache": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "GR": {"type": "string"},
                        "SiglaEstado": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "UO": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "ListaMunicipios": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "municipio": {"type": "string"},
                                    "siglaEstado": {"type": "string"}
                                },
                                "required": ["municipio", "siglaEstado"]
                            }
                        },
                        "regioes": {
                            "type": "array"
                        }
                    },
                    "required": ["GR", "SiglaEstado", "UO", "ListaMunicipios", "regioes"]
                }
            }
        },
        "required": ["TipoRequisicao", "RegioesCache"]
    }
}

# ----------------------------------------------------------------------------------------------
class PayloadError(Exception):
    """Custom exception for payload validation errors."""
    pass

# ----------------------------------------------------------------------------------------------
def extend_with_default(validator_class: jsonschema.validators.Draft7Validator) -> jsonschema.validators.Draft7Validator:
    """Extend a validator to apply defaults.
    
    :param validator_class: The validator class to extend.
    :return: The extended validator class.
    """
    
    validate_properties = validator_class.VALIDATORS["properties"]
    
    def set_defaults(validator, properties, instance, schema):
        if instance is None:
            instance = {}
            
        for property, subschema in properties.items():
            if "default" in subschema and instance is not None and property not in instance:
                instance[property] = subschema["default"]
                
        for error in validate_properties(validator, properties, instance, schema):
            yield error
            
    return validators.extend(validator_class, {"properties": set_defaults})

# ----------------------------------------------------------------------------------------------
def validate_and_apply_defaults(payload: dict) -> dict:
    """Validate payload and apply defaults based on request type.
    
    :param payload: JSON payload to validate.
    :return: JSON payload with defaults applied.
    :raises PayloadError: If payload is invalid.
    """

    DefaultValidator = extend_with_default(jsonschema.validators.Draft7Validator)
        
    try:
        try:
            req_type = payload["TipoRequisicao"]
        except KeyError:
            logging.error("Missing request type in payload.")
            raise PayloadError("Missing request type in payload.")
        
        try:
            validator = DefaultValidator(SCHEMAS[req_type])
        except KeyError:
            logging.error(f"Unsupported request type: {req_type}")
            raise PayloadError(f"Unsupported request type: {req_type}")
        
        try:
            validator.validate(payload)
            logging.info("Payload is valid.")
            return payload
        except jsonschema.exceptions.ValidationError as e:
            logging.error(f"Validation error: {e.message}")
            raise PayloadError(f"Validation error: {e.message}")
            
    except Exception as e:
        logging.error(f"Error processing payload: {str(e)}")
        raise PayloadError(f"Error processing payload: {str(e)}")