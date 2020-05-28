# ocrd_models

> OCR-D framework - file format APIs and schemas

See https://github.com/OCR-D/core

## Adding user methods to the generated PAGE API

Let's say you want to add a method `get_FirstTextRegion` on the pc:Page element:

1. Create a file `ocrd_models/ocrd_page_user_methods/get_FirstTextRegion.py`

```python
def get_FirstTextRegion(self):
  return self.get_TextRegion[0]
```

 **NOTE** The method name and file name must be identical.

 **NOTE** Do not use Python's `%` string interpolation operator, it will break generateDS. Use `"".format(...)` instead.

2. Edit `ocrd_models/ocrd_page_user_methods.py` and append to the `METHOD_SPECS` list:

```python
METHOD_SPECS = (
  # ...
  _add_method(r'^PageType$', 'get_FirstTextRegion')
  # ...
)
```

3. Regenerate the PAGE API:

```sh
make generate-page
```
