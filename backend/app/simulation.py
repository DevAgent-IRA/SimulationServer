@router.post("/simulate/unhandled/index_error")
def simulate_index_error():
    """
    Trigger an unhandled IndexError.
    """
    logger.info("triggering_unhandled_error", type="IndexError")
    my_list = [1, 2, 3]
    if len(my_list) > 10:
        return my_list[10]  # Crash
    else:
        return {"error": "Index out of bounds"}