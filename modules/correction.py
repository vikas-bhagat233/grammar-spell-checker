def apply_corrections(text, corrections):
    """
    Correction Engine / post-processing stage.

    This function takes spelling, grammar, and semantic findings and applies the
    best suggestions back to the original text. It sorts corrections from right to
    left to avoid offset shifts when replacing substrings.

    This is part of the final NLP pipeline stage: transform errors into corrected
    output, but it does not perform deep semantic or pragmatic understanding.
    """
    if not corrections:
        return text

    # Sort from right to left.
    # This prevents earlier replacements
    # from changing later positions.
    corrections = sorted(
        corrections,
        key=lambda x: (x["offset"], x["length"]),
        reverse=True
    )

    corrected = text

    occupied_ranges = []

    for correction in corrections:

        offset = correction["offset"]
        length = correction["length"]
        suggestion = correction.get("suggestion", "")

        if not suggestion:
            continue

        start = offset
        end = offset + length

        # Prevent overlapping corrections
        overlap = False

        for old_start, old_end in occupied_ranges:

            if start < old_end and end > old_start:
                overlap = True
                break

        if overlap:
            continue

        corrected = (
            corrected[:start]
            + suggestion
            + corrected[end:]
        )

        occupied_ranges.append((start, end))

    return corrected