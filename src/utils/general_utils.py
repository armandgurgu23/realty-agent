def parse_xml_content(xml_string:str, tag_name:str) -> str | None:
    """
    Extract the content from an XML tag in a string.
    
    Args:
        xml_string: String containing XML
        tag_name: Name of the XML tag to extract content from
    
    Returns:
        The content inside the XML tag, or None if tag not found
    """
    start_tag = f"<{tag_name}>"
    end_tag = f"</{tag_name}>"
    
    start_index = xml_string.find(start_tag)
    if start_index == -1:
        return None
    
    # Move past the opening tag
    content_start = start_index + len(start_tag)
    
    # Find the closing tag
    end_index = xml_string.find(end_tag, content_start)
    if end_index == -1:
        return None
    
    return xml_string[content_start:end_index]