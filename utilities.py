def data_height_to_points(figure, axis, data_height: float) -> float:
	# Convert a vertical world/data distance to matplotlib points
	pixel0 = axis.transData.transform((0.0, 0.0))[1]
	pixel1 = axis.transData.transform((0.0, data_height))[1]
	return abs(pixel1 - pixel0) * 72.0 / figure.dpi


def sync_linewidth_to_data(path_line, figure, axis, data_height: float) -> None:
	# Set a line's linewidth so it matches a distance in world/data units. 
	path_line.set_linewidth(data_height_to_points(figure, axis, data_height))
