"""
Advanced ML Service with ARIMA, Isolation Forest, Fourier, & Recommendations
"""
import numpy as np
from collections import Counter
import json
from scipy import signal, stats
from sklearn.ensemble import IsolationForest
import warnings
warnings.filterwarnings('ignore')

# Try to import statsmodels for ARIMA, fallback if not available
try:
    from statsmodels.tsa.arima.model import ARIMA
    HAS_ARIMA = True
except:
    HAS_ARIMA = False


class PowerAnalyzer:
    def __init__(self, values, timestamps=None):
        self.values = np.array(values)
        self.timestamps = timestamps or [None] * len(values)
        self.n = len(values)

    def get_global_stats(self):
        """Compute basic statistical metrics"""
        return {
            'mean': float(np.mean(self.values)),
            'std': float(np.std(self.values)),
            'median': float(np.median(self.values)),
            'min': float(np.min(self.values)),
            'max': float(np.max(self.values)),
            'p5': float(np.percentile(self.values, 5)),
            'p25': float(np.percentile(self.values, 25)),
            'p75': float(np.percentile(self.values, 75)),
            'p95': float(np.percentile(self.values, 95)),
            'count': int(self.n),
        }

    def classify_value(self, value, stats_dict):
        """Classify value as critical_low, low, normal, high, or critical_high"""
        mean, std = stats_dict['mean'], stats_dict['std']
        if value < mean - 2 * std:
            return 'critical_low'
        elif value < mean - std:
            return 'low'
        elif value > mean + 2 * std:
            return 'critical_high'
        elif value > mean + std:
            return 'high'
        return 'normal'

    def zscore_anomaly_detection(self):
        """Z-score based anomaly detection"""
        stats_dict = self.get_global_stats()
        mean, std = stats_dict['mean'], stats_dict['std']
        anomalies = []
        
        for i, v in enumerate(self.values):
            z_score = (v - mean) / (std + 1e-10)
            if abs(z_score) > 2.5:
                anomalies.append({'index': i, 'value': v, 'z_score': z_score, 'type': 'critical'})
            elif abs(z_score) > 1.5:
                anomalies.append({'index': i, 'value': v, 'z_score': z_score, 'type': 'warning'})
        
        return anomalies

    def isolation_forest_anomaly_detection(self, contamination=0.1):
        """Isolation Forest for anomaly detection (more robust than Z-score)"""
        if len(self.values) < 10:
            return []
        
        iso_forest = IsolationForest(contamination=min(contamination, 0.5), random_state=42)
        predictions = iso_forest.fit_predict(self.values.reshape(-1, 1))
        scores = iso_forest.score_samples(self.values.reshape(-1, 1))
        
        anomalies = []
        for i, (pred, score) in enumerate(zip(predictions, scores)):
            if pred == -1:  # -1 indicates anomaly
                anomalies.append({
                    'index': i,
                    'value': float(self.values[i]),
                    'anomaly_score': float(score),
                    'type': 'anomaly'
                })
        
        return sorted(anomalies, key=lambda x: x['anomaly_score'])[:10]  # Top 10

    def fourier_analysis(self):
        """Fourier Transform to detect cyclic patterns"""
        if len(self.values) < 4:
            return {}
        
        fft = np.fft.fft(self.values - np.mean(self.values))
        freqs = np.fft.fftfreq(len(self.values))
        power = np.abs(fft) ** 2
        
        # Find dominant frequencies
        top_indices = np.argsort(power)[-5:][::-1]
        dominant_freq = []
        
        for idx in top_indices:
            if freqs[idx] > 0:  # Only positive frequencies
                dominant_freq.append({
                    'frequency': float(freqs[idx]),
                    'power': float(power[idx])
                })
        
        return {
            'dominant_frequencies': dominant_freq,
            'has_cycles': len(dominant_freq) > 0
        }

    def arima_forecast(self, periods=10):
        """ARIMA-based time series forecasting"""
        if not HAS_ARIMA or len(self.values) < 10:
            return self._exponential_smoothing_forecast(periods)
        
        try:
            model = ARIMA(self.values, order=(1, 1, 1))
            results = model.fit()
            forecast = results.get_forecast(steps=periods)
            
            return {
                'forecast': forecast.predicted_mean.tolist(),
                'confidence_lower': forecast.conf_int().iloc[:, 0].tolist(),
                'confidence_upper': forecast.conf_int().iloc[:, 1].tolist(),
                'method': 'ARIMA'
            }
        except:
            return self._exponential_smoothing_forecast(periods)

    def _exponential_smoothing_forecast(self, periods=10):
        """Fallback exponential smoothing forecast"""
        alpha = 0.3
        forecast = []
        last_value = self.values[-1]
        
        for _ in range(periods):
            last_value = alpha * self.values[-1] + (1 - alpha) * last_value
            forecast.append(float(last_value))
        
        return {
            'forecast': forecast,
            'method': 'Exponential Smoothing'
        }

    def get_trend_analysis(self):
        """Linear regression trend analysis"""
        x = np.arange(len(self.values))
        coeffs = np.polyfit(x, self.values, 1)
        slope, intercept = coeffs[0], coeffs[1]
        
        # Predict next value
        next_val = slope * len(self.values) + intercept
        
        trend = 'stable'
        if slope > 0.0002:
            trend = 'increasing'
        elif slope < -0.0002:
            trend = 'decreasing'
        
        return {
            'slope': float(slope),
            'intercept': float(intercept),
            'next_predicted_value': float(next_val),
            'trend': trend
        }

    def build_transition_matrix(self):
        """Markov chain state transitions"""
        stats_dict = self.get_global_stats()
        labels = [self.classify_value(v, stats_dict) for v in self.values]
        classes = ['critical_low', 'low', 'normal', 'high', 'critical_high']
        matrix = {c: {c2: 0 for c2 in classes} for c in classes}
        
        for i in range(1, len(labels)):
            matrix[labels[i-1]][labels[i]] += 1
        
        for row in matrix:
            total = sum(matrix[row].values())
            if total > 0:
                for col in matrix[row]:
                    matrix[row][col] = round(matrix[row][col] / total, 4)
        
        return matrix

    def compute_stability_score(self):
        """Compute 0-100 stability score"""
        stats_dict = self.get_global_stats()
        mean = stats_dict['mean']
        std = stats_dict['std']
        
        cv = std / (mean + 1e-10)
        anomaly_count = len(self.zscore_anomaly_detection())
        anomaly_rate = anomaly_count / len(self.values)
        
        range_score = 1 - min((stats_dict['max'] - stats_dict['min']) / (mean * 0.1 + 0.001), 1)
        
        stability = (1 - min(cv * 10, 1)) * 0.4 + (1 - anomaly_rate) * 0.4 + range_score * 0.2
        return round(float(stability * 100), 1)

    def get_recommendations(self, daily_cost, monthly_cost, stability_score, anomaly_count):
        """Generate actionable recommendations"""
        recommendations = []
        
        # Cost recommendations
        if monthly_cost > 5000:
            recommendations.append({
                'category': 'cost',
                'severity': 'high',
                'message': f'This appliance costs ₦{monthly_cost:.0f}/month. Consider usage optimization.',
                'action': 'Reduce peak-hour usage'
            })
        elif monthly_cost > 2000:
            recommendations.append({
                'category': 'cost',
                'severity': 'medium',
                'message': f'Moderate cost of ₦{monthly_cost:.0f}/month. Could optimize.',
                'action': 'Monitor during peak hours'
            })
        else:
            recommendations.append({
                'category': 'cost',
                'severity': 'low',
                'message': f'Low cost of ₦{monthly_cost:.0f}/month. Usage is efficient.',
                'action': 'Continue current usage'
            })
        
        # Stability recommendations
        if stability_score >= 80:
            recommendations.append({
                'category': 'stability',
                'severity': 'low',
                'message': f'Excellent stability ({stability_score}/100). System is reliable.',
                'action': 'No action needed'
            })
        elif stability_score >= 60:
            recommendations.append({
                'category': 'stability',
                'severity': 'medium',
                'message': f'Good stability ({stability_score}/100). Minor fluctuations detected.',
                'action': 'Monitor for changes'
            })
        else:
            recommendations.append({
                'category': 'stability',
                'severity': 'high',
                'message': f'Low stability ({stability_score}/100). Frequent spikes detected.',
                'action': 'Check wiring and connections'
            })
        
        # Anomaly recommendations
        if anomaly_count > 10:
            recommendations.append({
                'category': 'anomaly',
                'severity': 'high',
                'message': f'{anomaly_count} anomalies detected. May indicate a fault.',
                'action': 'Investigate power source'
            })
        elif anomaly_count > 3:
            recommendations.append({
                'category': 'anomaly',
                'severity': 'medium',
                'message': f'{anomaly_count} anomalies detected. Worth investigating.',
                'action': 'Monitor for patterns'
            })
        else:
            recommendations.append({
                'category': 'anomaly',
                'severity': 'low',
                'message': 'Minimal anomalies. Normal operation.',
                'action': 'No action needed'
            })
        
        return recommendations

    def full_analysis(self, tariff=68, wattage=0, session_hours=1):
        """Run complete analysis pipeline"""
        stats_dict = self.get_global_stats()
        
        # Detection methods
        zscore_anomalies = self.zscore_anomaly_detection()
        isolation_anomalies = self.isolation_forest_anomaly_detection()
        
        # Advanced analytics
        fourier = self.fourier_analysis()
        trend = self.get_trend_analysis()
        forecast = self.arima_forecast(periods=10)
        transition_matrix = self.build_transition_matrix()
        stability = self.compute_stability_score()
        
        # Cost estimation
        avg_power_w = wattage if wattage > 0 else stats_dict['mean']
        session_kwh = (avg_power_w * session_hours) / 1000
        session_cost = session_kwh * tariff
        daily_kwh = avg_power_w * 8 / 1000  # Assume 8h/day
        daily_cost = daily_kwh * tariff
        monthly_cost = daily_cost * 30
        
        # Recommendations
        recommendations = self.get_recommendations(
            daily_cost, monthly_cost, stability, len(zscore_anomalies)
        )
        
        return {
            'version': '2.0',
            'global_stats': stats_dict,
            'zscore_anomalies': zscore_anomalies,
            'isolation_forest_anomalies': isolation_anomalies,
            'fourier_analysis': fourier,
            'trend_analysis': trend,
            'forecast': forecast,
            'transition_matrix': transition_matrix,
            'stability_score': stability,
            'cost_analysis': {
                'session_kwh': session_kwh,
                'session_cost': session_cost,
                'daily_cost': daily_cost,
                'monthly_cost': monthly_cost
            },
            'recommendations': recommendations
        }
