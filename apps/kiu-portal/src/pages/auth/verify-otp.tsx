import { useState, useRef, useEffect, useCallback } from 'react';
import { useLocation, Link } from 'wouter';
import { Button, Card } from '@/components/ui/shared';
import { useToast } from '@/hooks/use-toast';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldCheck, RefreshCw, ArrowLeft, Mail } from 'lucide-react';

const BASE = import.meta.env.BASE_URL.replace(/\/$/, "");

export default function VerifyOtp() {
  const [, setLocation] = useLocation();
  const { toast } = useToast();

  const [digits, setDigits] = useState<string[]>(Array(6).fill(""));
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [cooldown, setCooldown] = useState(0);
  const [success, setSuccess] = useState(false);

  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);
  const cooldownRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const email = localStorage.getItem("kiu_pending_email") || "";

  useEffect(() => {
    if (!email) {
      setLocation("/register");
      return;
    }
    inputRefs.current[0]?.focus();
  }, [email, setLocation]);

  // Cleanup interval on unmount
  useEffect(() => () => { if (cooldownRef.current) clearInterval(cooldownRef.current); }, []);

  const startCooldown = useCallback((seconds: number) => {
    setCooldown(seconds);
    if (cooldownRef.current) clearInterval(cooldownRef.current);
    cooldownRef.current = setInterval(() => {
      setCooldown((prev) => {
        if (prev <= 1) {
          if (cooldownRef.current) clearInterval(cooldownRef.current);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  }, []);

  const handleChange = (idx: number, value: string) => {
    const char = value.replace(/\D/g, "").slice(-1);
    const next = [...digits];
    next[idx] = char;
    setDigits(next);
    if (char && idx < 5) {
      inputRefs.current[idx + 1]?.focus();
    }
  };

  const handleKeyDown = (idx: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace" && !digits[idx] && idx > 0) {
      inputRefs.current[idx - 1]?.focus();
    }
    if (e.key === "ArrowLeft" && idx > 0) inputRefs.current[idx - 1]?.focus();
    if (e.key === "ArrowRight" && idx < 5) inputRefs.current[idx + 1]?.focus();
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
    const next = [...digits];
    pasted.split("").forEach((c, i) => { if (i < 6) next[i] = c; });
    setDigits(next);
    const focusIdx = Math.min(pasted.length, 5);
    inputRefs.current[focusIdx]?.focus();
  };

  const handleVerify = async () => {
    const code = digits.join("");
    if (code.length < 6) {
      toast({ title: "Incomplete code", description: "Please enter all 6 digits.", variant: "destructive" });
      return;
    }

    setIsLoading(true);
    try {
      const res = await fetch(`${BASE}/api/auth/verify-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, code }),
      });
      const json = await res.json();

      if (!res.ok) {
        toast({
          title: res.status === 410 ? "Code expired" : "Invalid code",
          description: json.message || "Please try again.",
          variant: "destructive",
        });
        if (res.status === 410) {
          setDigits(Array(6).fill(""));
          inputRefs.current[0]?.focus();
        }
        return;
      }

      // Success - redirect to login page for user to sign in
      setSuccess(true);
      localStorage.removeItem("kiu_pending_email");

      setTimeout(() => {
        setLocation("/login");
      }, 1200);
    } catch {
      toast({ title: "Network error", description: "Could not connect to the server.", variant: "destructive" });
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    if (cooldown > 0) return;
    setIsResending(true);
    try {
      const res = await fetch(`${BASE}/api/auth/resend-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email }),
      });
      const json = await res.json();

      if (res.status === 429) {
        startCooldown(json.retryAfter || 60);
        toast({ title: "Please wait", description: json.message, variant: "destructive" });
        return;
      }

      if (!res.ok) {
        toast({ title: "Error", description: json.message || "Could not resend OTP.", variant: "destructive" });
        return;
      }

      startCooldown(60);
      setDigits(Array(6).fill(""));
      inputRefs.current[0]?.focus();
      toast({ title: "Code resent!", description: "Check your email or the server terminal." });
    } catch {
      toast({ title: "Network error", description: "Could not connect.", variant: "destructive" });
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="min-h-[90vh] flex items-center justify-center p-4 relative">
      <div className="absolute inset-0 z-0 opacity-40 mix-blend-multiply">
        <img src={`${import.meta.env.BASE_URL}images/abstract-academic.png`} alt="" className="w-full h-full object-cover" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md relative z-10"
      >
        <Link href="/register" className="inline-flex items-center text-sm font-semibold text-muted-foreground hover:text-primary mb-6 transition-colors">
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to Register
        </Link>

        <Card className="p-8 shadow-2xl shadow-primary/10 border-white/50 bg-white/90 backdrop-blur-xl">
          <AnimatePresence mode="wait">
            {success ? (
              <motion.div
                key="success"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-center py-8 space-y-4"
              >
                <div className="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center mx-auto">
                  <ShieldCheck className="w-10 h-10 text-green-600" />
                </div>
                <h2 className="text-2xl font-bold text-green-700">Verified!</h2>
                <p className="text-muted-foreground">Your account is confirmed. Redirecting…</p>
              </motion.div>
            ) : (
              <motion.div key="form" className="space-y-6">
                <div className="text-center">
                  <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
                    <Mail className="w-8 h-8 text-primary" />
                  </div>
                  <h1 className="text-2xl font-display font-bold text-primary">Verify Your Email</h1>
                  <p className="text-muted-foreground text-sm mt-2">
                    Enter the 6-digit code sent to
                  </p>
                  <p className="font-semibold text-foreground text-sm">{email}</p>
                </div>

                {/* OTP digit inputs */}
                <div className="flex gap-2 justify-center" onPaste={handlePaste}>
                  {digits.map((d, i) => (
                    <input
                      key={i}
                      ref={(el) => { inputRefs.current[i] = el; }}
                      type="text"
                      inputMode="numeric"
                      maxLength={1}
                      value={d}
                      onChange={(e) => handleChange(i, e.target.value)}
                      onKeyDown={(e) => handleKeyDown(i, e)}
                      className={`w-11 h-14 text-center text-xl font-bold rounded-xl border-2 outline-none transition-all
                        ${d ? "border-primary bg-primary/5 text-primary" : "border-border bg-white text-foreground"}
                        focus:border-primary focus:ring-2 focus:ring-primary/20`}
                    />
                  ))}
                </div>

                <Button
                  className="w-full py-5 text-base"
                  onClick={handleVerify}
                  isLoading={isLoading}
                  disabled={isLoading || digits.join("").length < 6}
                >
                  Verify Account
                </Button>

                <div className="text-center text-sm text-muted-foreground">
                  Didn't receive the code?{" "}
                  {cooldown > 0 ? (
                    <span className="text-muted-foreground font-medium">Resend in {cooldown}s</span>
                  ) : (
                    <button
                      onClick={handleResend}
                      disabled={isResending}
                      className="font-bold text-primary hover:underline inline-flex items-center gap-1 disabled:opacity-50"
                    >
                      {isResending && <RefreshCw className="w-3 h-3 animate-spin" />}
                      Resend OTP
                    </button>
                  )}
                </div>

                <p className="text-xs text-muted-foreground text-center">
                  No email? Check the server terminal — your OTP is always printed there.
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </Card>
      </motion.div>
    </div>
  );
}
