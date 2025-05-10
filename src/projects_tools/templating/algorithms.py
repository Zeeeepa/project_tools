"""
Algorithms for template generation.

This module provides algorithms for generating content programmatically.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


def generate_crud_operations(model_name: str, fields: List[Dict[str, Any]]) -> str:
    """
    Generate CRUD operations for a model.
    
    Args:
        model_name: Name of the model
        fields: List of field definitions
        
    Returns:
        Generated CRUD operations code
    """
    # Generate imports
    imports = [
        "from sqlalchemy.orm import Session",
        f"from models.{model_name.lower()} import {model_name}",
        "from typing import List, Optional, Dict, Any"
    ]
    
    # Generate field validation
    field_validations = []
    for field in fields:
        field_name = field.get('name')
        field_type = field.get('type', 'str')
        required = field.get('required', False)
        
        if required:
            field_validations.append(f"    if '{field_name}' not in data:")
            field_validations.append(f"        raise ValueError(\"'{field_name}' is required\")")
            
        if field_type == 'int':
            field_validations.append(f"    if '{field_name}' in data and not isinstance(data['{field_name}'], int):")
            field_validations.append(f"        raise ValueError(\"'{field_name}' must be an integer\")")
        elif field_type == 'float':
            field_validations.append(f"    if '{field_name}' in data and not isinstance(data['{field_name}'], (int, float)):")
            field_validations.append(f"        raise ValueError(\"'{field_name}' must be a number\")")
        elif field_type == 'bool':
            field_validations.append(f"    if '{field_name}' in data and not isinstance(data['{field_name}'], bool):")
            field_validations.append(f"        raise ValueError(\"'{field_name}' must be a boolean\")")
    
    # Generate create function
    create_function = f"""
def create_{model_name.lower()}(db: Session, data: Dict[str, Any]) -> {model_name}:
    \"\"\"
    Create a new {model_name}.
    
    Args:
        db: Database session
        data: Data for the new {model_name}
        
    Returns:
        Created {model_name}
    \"\"\"
{"".join(f"    {line}\n" for line in field_validations)}
    db_obj = {model_name}(**data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
"""
    
    # Generate get function
    get_function = f"""
def get_{model_name.lower()}(db: Session, {model_name.lower()}_id: int) -> Optional[{model_name}]:
    \"\"\"
    Get a {model_name} by ID.
    
    Args:
        db: Database session
        {model_name.lower()}_id: ID of the {model_name}
        
    Returns:
        {model_name} or None if not found
    \"\"\"
    return db.query({model_name}).filter({model_name}.id == {model_name.lower()}_id).first()
"""
    
    # Generate get all function
    get_all_function = f"""
def get_all_{model_name.lower()}s(db: Session, skip: int = 0, limit: int = 100) -> List[{model_name}]:
    \"\"\"
    Get all {model_name}s.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of {model_name}s
    \"\"\"
    return db.query({model_name}).offset(skip).limit(limit).all()
"""
    
    # Generate update function
    update_function = f"""
def update_{model_name.lower()}(db: Session, {model_name.lower()}_id: int, data: Dict[str, Any]) -> Optional[{model_name}]:
    \"\"\"
    Update a {model_name}.
    
    Args:
        db: Database session
        {model_name.lower()}_id: ID of the {model_name}
        data: Data to update
        
    Returns:
        Updated {model_name} or None if not found
    \"\"\"
    db_obj = get_{model_name.lower()}(db, {model_name.lower()}_id)
    if db_obj is None:
        return None
        
    for key, value in data.items():
        setattr(db_obj, key, value)
        
    db.commit()
    db.refresh(db_obj)
    return db_obj
"""
    
    # Generate delete function
    delete_function = f"""
def delete_{model_name.lower()}(db: Session, {model_name.lower()}_id: int) -> bool:
    \"\"\"
    Delete a {model_name}.
    
    Args:
        db: Database session
        {model_name.lower()}_id: ID of the {model_name}
        
    Returns:
        True if deleted, False if not found
    \"\"\"
    db_obj = get_{model_name.lower()}(db, {model_name.lower()}_id)
    if db_obj is None:
        return False
        
    db.delete(db_obj)
    db.commit()
    return True
"""
    
    # Combine everything
    return "\n".join(imports) + create_function + get_function + get_all_function + update_function + delete_function


def generate_form_validation(form_name: str, fields: List[Dict[str, Any]]) -> str:
    """
    Generate form validation code.
    
    Args:
        form_name: Name of the form
        fields: List of field definitions
        
    Returns:
        Generated form validation code
    """
    # Generate imports
    imports = [
        "import { useState } from 'react';",
        "import { z } from 'zod';",
    ]
    
    # Generate schema
    schema_fields = []
    for field in fields:
        field_name = field.get('name')
        field_type = field.get('type', 'string')
        required = field.get('required', False)
        min_length = field.get('min_length')
        max_length = field.get('max_length')
        pattern = field.get('pattern')
        
        if field_type == 'string':
            schema_field = f"  {field_name}: z.string()"
            
            if required:
                schema_field += ".nonempty(`${field_name} is required`)"
            else:
                schema_field += ".optional()"
                
            if min_length:
                schema_field += f".min({min_length}, `${field_name} must be at least {min_length} characters`)"
                
            if max_length:
                schema_field += f".max({max_length}, `${field_name} must be at most {max_length} characters`)"
                
            if pattern:
                schema_field += f".regex(/{pattern}/, `${field_name} is not valid`)"
                
            schema_fields.append(schema_field)
        elif field_type == 'number':
            schema_field = f"  {field_name}: z.number()"
            
            if required:
                schema_field += ".defined(`${field_name} is required`)"
            else:
                schema_field += ".optional()"
                
            if 'min' in field:
                schema_field += f".min({field['min']}, `${field_name} must be at least {field['min']}`)"
                
            if 'max' in field:
                schema_field += f".max({field['max']}, `${field_name} must be at most {field['max']}`)"
                
            schema_fields.append(schema_field)
        elif field_type == 'boolean':
            schema_field = f"  {field_name}: z.boolean()"
            
            if required:
                schema_field += ".defined(`${field_name} is required`)"
            else:
                schema_field += ".optional()"
                
            schema_fields.append(schema_field)
        elif field_type == 'email':
            schema_field = f"  {field_name}: z.string().email(`${field_name} must be a valid email`)"
            
            if required:
                schema_field += ".nonempty(`${field_name} is required`)"
            else:
                schema_field += ".optional()"
                
            schema_fields.append(schema_field)
    
    schema = f"""
const {form_name}Schema = z.object({{
    {'\n'.join(schema_fields)}
}});
"""
    
    # Generate hook
    initial_values = ", ".join([f"{field['name']}: {get_default_value(field)}" for field in fields])
    
    hook = f"""
export function use{form_name}Validation() {{
  const [values, setValues] = useState({{ {initial_values} }});
  const [errors, setErrors] = useState({{}});
  const [touched, setTouched] = useState({{}});
  
  const handleChange = (e) => {{
    const {{ name, value, type, checked }} = e.target;
    const fieldValue = type === 'checkbox' ? checked : value;
    
    setValues(prev => ({{
      ...prev,
      [name]: fieldValue
    }}));
    
    // Validate field
    try {{
      {form_name}Schema.shape[name].parse(fieldValue);
      setErrors(prev => ({{ ...prev, [name]: undefined }}));
    }} catch (error) {{
      setErrors(prev => ({{ ...prev, [name]: error.errors[0].message }}));
    }}
  }};
  
  const handleBlur = (e) => {{
    const {{ name }} = e.target;
    
    setTouched(prev => ({{
      ...prev,
      [name]: true
    }}));
  }};
  
  const validateForm = () => {{
    try {{
      {form_name}Schema.parse(values);
      return true;
    }} catch (error) {{
      const formattedErrors = {{}};
      error.errors.forEach(err => {{
        formattedErrors[err.path[0]] = err.message;
      }});
      setErrors(formattedErrors);
      return false;
    }}
  }};
  
  const resetForm = () => {{
    setValues({{ {initial_values} }});
    setErrors({{}});
    setTouched({{}});
  }};
  
  return {{
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    validateForm,
    resetForm
  }};
}}
"""
    
    # Combine everything
    return "\n".join(imports) + schema + hook


def get_default_value(field: Dict[str, Any]) -> str:
    """
    Get default value for a field.
    
    Args:
        field: Field definition
        
    Returns:
        Default value as a string
    """
    field_type = field.get('type', 'string')
    default = field.get('default')
    
    if default is not None:
        if field_type == 'string' or field_type == 'email':
            return f"'{default}'"
        else:
            return str(default)
    
    if field_type == 'string' or field_type == 'email':
        return "''"
    elif field_type == 'number':
        return "0"
    elif field_type == 'boolean':
        return "false"
    else:
        return "''"
