
Description of the keys in the section of a parameter/attribute:

- **type:** specifies the datatype of the parameter/attribute. Valid data types are:

   Simple data types:
    - *bool* - a boolean value
    - *int* - an integer value
    - *scene* - an integer in the range between 0 and 255, representing a scene number
    - *float* - a float value
    - *num* - an equivalent to float
    - *str* - a string
    - *ip* - a string, representing a hostname, an ipv4-address or an ipv6-address
    - *ipv4* - a string, representing strictly an ipv4-address
    - *ipv6* - a string, representing strictly an ipv6-address
    - *mac* - a string, representing a mac-address
    - *knx_ga* - a string, representing a KNX group address (eg.: 31/7/255)
    - *foo* - the universal datatype

   Complex data types:
    - *dict* - a dictionary
    - *list* - a list with each entry of the datatype **foo**
    - *list(len)* - a list of a fixed length **len** must be an integer value > 0
    - *list(subtype)* - a list with each entry of the same specified subtype :sup:`1` (e.g: *list(int)*
      or *list(ipv4)*)
    - *list(subtype, subtype, ...)* - a list with each entry of a specified type. If the list
      is longer than the given list of subtypes :sup:`1`, the last given subtype will be used for all
      subsequent list entries.
    - *list(len,subtype, subtype, ...)* - a list of a fixed length with each entry of a specified
      type. If the list is longer than the given list of subtypes :sup:`1`  the last given subtype will
      be used for all subsequent list entries.

    :sup:`1` *subtype* can only be a simple datatype

- **default:** Optional: Specifies the default value to be used, if no value is given in in the
  configuration file `/etc/plugin.yaml` or `/etc/module.yaml`

- **description:** is a multi language text. - The texts in the different languages are specified
  in sub-entries in the form <language>: <text>. Use the standard two letter codes for specifying
  the language (de, en, fr, pl, ..). **de** and **en** are required. Other languages are optional

- **valid_list:** Optional: List of allowed values for the parameter

- **valid_list_description:** Optional: Descriptions of the allowed values defined in **valid_list:**
  if defined, it has to have sub-keys for the different languages (de, en, fr, pl, ..). **de** and **en**
  are required. Other languages are optional. Each language sub-key has to be a list with each entry describing
  the corresponding entry in **valid_list:**.

- **valid_min:** Optional: For data types *int*, *pint*, *float*, *pfloat*, *num* and *scene*:
  minimum allowed value for the parameter

- **valid_max:** Optional: For data types *int*, *pint*, *float*, *pfloat*, *num* and *scene*:
  maximum allowed value for the parameter

- **mandatory:** Optional: If set to True, a value must be configured for the plugin/module to
  get loaded an initialized. If a value for a parameter that is marked as mandatory is missing,
  the plugin will not be loaded.

