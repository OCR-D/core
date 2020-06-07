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

2. Edit `ocrd_models/ocrd_page_user_methods.py` and append to the `METHOD_SPECS` list:

```python
METHOD_SPECS = (
  # ...
  _add_method(r'^PageType$', 'get_FirstTextRegion')
  # ...
)
```

If the filename (sans the `.py` extension) does not match the method_name, you
can provide an additional `file_name` attribute to `_add_method`:

```python
METHOD_SPECS = (
  # ...
  _add_method(r'^PageType$', 'exportChildren', 'exportChildren_PageType')
  # ...
)
```

Would add the method `exportChildren` from a file `exportChildren_PageType.py`.

**NOTE** The method name in the file must match the method name passed to
`_add_method`. This is *not* checked automatically, so double-check manually!


3. Regenerate the PAGE API:

```sh
make generate-page
```
