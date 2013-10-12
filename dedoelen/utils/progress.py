
from progressbar import ProgressBar, Percentage, Bar, Timer

class AdaptiveETA(Timer):
    """
    """
    TIME_SENSITIVE = True
    NUM_SAMPLES = 10

    def _update_samples(self, currval, elapsed):
        sample = (currval, elapsed)
        if not hasattr(self, 'samples'):
            self.samples = [sample] * (self.NUM_SAMPLES + 1)
        else:
            self.samples.append(sample)
        return self.samples.pop(0)

    def _eta(self, maxval, currval, elapsed):
        return elapsed * maxval / float(currval) - elapsed

    def update(self, pbar):
        """
        """
        if pbar.currval == 0:
            return 'ETA: --:--:--'
        elif pbar.finished:
            return 'Time: %s' % self.format_time(pbar.seconds_elapsed)
        else:
            elapsed = pbar.seconds_elapsed
            currval1, elapsed1 = self._update_samples(pbar.currval, elapsed)
            eta = self._eta(pbar.maxval, pbar.currval, elapsed)
            if pbar.currval > currval1:
                etasamp = self._eta(pbar.maxval - currval1, pbar.currval -
                        currval1, elapsed - elapsed1)
                weight = (pbar.currval / float(pbar.maxval)) ** 0.5
                eta = (1 - weight) * eta + weight * etasamp
            return 'ETA: %s' %  self.format_time(eta)

ophaal_progress = ProgressBar(widgets=['Opgehaald: ', Percentage(), ' ', Bar(),
    ' ', AdaptiveETA()])
