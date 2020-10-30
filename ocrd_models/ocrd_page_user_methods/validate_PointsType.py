def validate_PointsType(self, value):
    """
    Improved validation of @points
    """
    # 8<-- original
    # Validate type pc:PointsType, a restriction on string.
    print('value=%s Validate_simpletypes_=%s gds_collector_=%s' % (value, Validate_simpletypes_, self.gds_collector_))
    if not value or not Validate_simpletypes_ or not self.gds_collector_:
        return True
    if not isinstance(value, str):
        lineno = self.gds_get_node_lineno_()
        self.gds_collector_.add_message('Value "%(value)s"%(lineno)s is not of the correct base simple type (str)' % {"value": value, "lineno": lineno, })
        return False
    if not self.gds_validate_simple_patterns(self.validate_PointsType_patterns_, value):
        self.gds_collector_.add_message('Value "%s" does not match xsd pattern restrictions: %s' % (value, self.validate_PointsType_patterns_, ))
    # -->8 original
    for idx, xy in enumerate(value.split(' ')):
        x, y = [int(v) for v in  xy.split(',')]
        if x < 0: self.gds_collector_.add_message('Negative x coordinate at position %d in "%s"' % (idx, value))
        if y < 0: self.gds_collector_.add_message('Negative y coordinate at position %d in "%s"' % (idx, value))

