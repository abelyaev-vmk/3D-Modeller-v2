class CameraInformation:
    def __init__(self, calibration=None, projection=None, model_view=None, save_path=None):
        self.calibration = calibration
        self.projection = projection
        self.model_view = model_view
        self.save_path = save_path

    def save(self, save_path=None):
        path = save_path if save_path else self.save_path
        with open(path, "w") as f:
            for matr in [self.calibration, self.projection, self.model_view]:
                for i in range(matr.shape[0]):
                    for j in range(matr.shape[1]):
                        f.write(matr[i, j].__str__() + " ")
                if matr.shape[0] == 3:
                    for j in [0, 0, 0, 1]:
                        f.write(j.__str__() + " ")
                f.write("\n")

