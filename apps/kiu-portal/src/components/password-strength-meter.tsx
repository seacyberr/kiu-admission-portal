import React, { useMemo } from 'react';
import { CheckCircle2, XCircle } from 'lucide-react';

interface PasswordStrengthMeterProps {
  password: string;
}

export function PasswordStrengthMeter({ password }: PasswordStrengthMeterProps) {
  const strength = useMemo(() => {
    if (!password) return 0;
    
    let score = 0;
    
    // Length check
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (password.length >= 16) score++;
    
    // Uppercase check
    if (/[A-Z]/.test(password)) score++;
    
    // Lowercase check
    if (/[a-z]/.test(password)) score++;
    
    // Number check
    if (/\d/.test(password)) score++;
    
    // Special character check
    if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) score++;
    
    return Math.min(score, 5);
  }, [password]);

  const getStrengthLabel = () => {
    switch (strength) {
      case 0:
        return 'No password';
      case 1:
        return 'Very weak';
      case 2:
        return 'Weak';
      case 3:
        return 'Fair';
      case 4:
        return 'Good';
      case 5:
        return 'Strong';
      default:
        return 'Unknown';
    }
  };

  const getStrengthColor = () => {
    switch (strength) {
      case 0:
        return 'bg-gray-300';
      case 1:
        return 'bg-red-500';
      case 2:
        return 'bg-orange-500';
      case 3:
        return 'bg-yellow-500';
      case 4:
        return 'bg-lime-500';
      case 5:
        return 'bg-green-500';
      default:
        return 'bg-gray-300';
    }
  };

  const requirements = [
    {
      label: 'At least 8 characters',
      met: password.length >= 8,
    },
    {
      label: 'Uppercase letter',
      met: /[A-Z]/.test(password),
    },
    {
      label: 'Lowercase letter',
      met: /[a-z]/.test(password),
    },
    {
      label: 'Number',
      met: /\d/.test(password),
    },
    {
      label: 'Special character',
      met: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password),
    },
  ];

  if (!password) {
    return null;
  }

  return (
    <div className="space-y-3 mt-3">
      {/* Strength bar */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <label className="text-xs font-semibold text-foreground">Password strength</label>
          <span className={`text-xs font-bold ${
            strength === 0 ? 'text-gray-500' :
            strength === 1 ? 'text-red-600' :
            strength === 2 ? 'text-orange-600' :
            strength === 3 ? 'text-yellow-600' :
            strength === 4 ? 'text-lime-600' :
            'text-green-600'
          }`}>
            {getStrengthLabel()}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
          <div
            className={`h-full transition-all duration-300 ${getStrengthColor()}`}
            style={{ width: `${(strength / 5) * 100}%` }}
          />
        </div>
      </div>

      {/* Requirements checklist */}
      <div className="space-y-2">
        <p className="text-xs font-semibold text-foreground">Requirements:</p>
        <ul className="space-y-1">
          {requirements.map((req, idx) => (
            <li key={idx} className="flex items-center gap-2 text-xs">
              {req.met ? (
                <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0" />
              ) : (
                <XCircle className="w-4 h-4 text-gray-300 flex-shrink-0" />
              )}
              <span className={req.met ? 'text-green-700' : 'text-gray-500'}>
                {req.label}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
