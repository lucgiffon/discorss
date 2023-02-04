def get_or_create(session, model, **kwargs):
    """
    Source: https://stackoverflow.com/a/6078058/4803860
    Parameters
    ----------
    session
        SQLAlchemy session object.
    model
        The model class to which the object belong.
    kwargs
        The parameters of the object to retrieve.

    Returns
    -------
        object of class `model` from the database if it already exists (based on provided parameters)
        or create it if it does not.
    """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance