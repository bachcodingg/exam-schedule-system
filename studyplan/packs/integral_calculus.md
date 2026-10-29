---
course: Integral Calculus
match: integral calculus, integraalilaskenta, integral calculation, bm20a8100
---

# Topic: Techniques refresher
keywords: technique, refresher, parts, trig identit, partial fraction

## Overview

Integration undoes differentiation: $\int f(x)\,dx = F(x) + C$ means $F'(x) = f(x)$. You can
always check an answer by differentiating it. Almost every exam integral is solved with one of
five moves. Learn to **recognise which one** before you write anything:

| You see | Move | Idea |
|---|---|---|
| a table form: $x^n$, $e^x$, $\sin x$, $\frac{1}{x}$, $\frac{1}{1+x^2}$ | table | $\int x^n dx = \frac{x^{n+1}}{n+1}$ ($n \ne -1$), $\int \frac{dx}{x} = \ln\lvert x\rvert$ |
| a function *inside* another, and the inner derivative as a factor: $f(g(x))\,g'(x)$ | substitution | $u = g(x)$, $du = g'(x)\,dx$ |
| a product of two different kinds: $x e^x$, $x \sin x$, $x \ln x$, $e^x \sin x$ | integration by parts | $\int u\,dv = uv - \int v\,du$ |
| powers of $\sin$ and $\cos$ | trig identity | $\sin^2 x = \frac{1-\cos 2x}{2}$, $\cos^2 x = \frac{1+\cos 2x}{2}$, $\sin^2 + \cos^2 = 1$ |
| a fraction of polynomials whose denominator factors | partial fractions | $\frac{1}{(x-a)(x-b)} = \frac{A}{x-a} + \frac{B}{x-b}$ |

**Choosing $u$ for integration by parts (LIATE).** Pick as $u$ the function that comes first in
**L**ogarithm, **I**nverse trig, **A**lgebraic ($x^n$), **T**rig, **E**xponential. The rest is
$dv$. The goal: $u$ gets simpler when differentiated, $dv$ stays easy to integrate.

**Odd power of $\sin$ or $\cos$:** split one factor off and turn the rest with
$\sin^2 = 1 - \cos^2$, then substitute $u = \cos x$ (or $u = \sin x$).

## Worked examples

### Example 1: integration by parts, $\int x e^{2x}\,dx$

Product of algebraic and exponential: parts, with $u = x$ (A before E).

- $u = x \Rightarrow du = dx$; $dv = e^{2x} dx \Rightarrow v = \frac{1}{2} e^{2x}$.
- $\int x e^{2x} dx = \frac{x}{2} e^{2x} - \int \frac{1}{2} e^{2x} dx = \frac{x}{2} e^{2x} - \frac{1}{4} e^{2x} + C$.
- **Check:** $\frac{d}{dx}\left(\frac{x}{2} e^{2x} - \frac{1}{4} e^{2x}\right) = \frac{1}{2}e^{2x} + x e^{2x} - \frac{1}{2} e^{2x} = x e^{2x}$. ✓

*Why it works:* differentiating $x$ removes it, and $e^{2x}$ integrates to itself (times $\frac12$).

### Example 2: substitution, $\int x\sqrt{x^2 + 9}\,dx$

Inside function $x^2 + 9$, its derivative $2x$ is (up to a constant) the factor $x$.

- $u = x^2 + 9$, $du = 2x\,dx$, so $x\,dx = \frac{1}{2} du$.
- $\int x\sqrt{x^2+9}\,dx = \frac{1}{2}\int u^{1/2} du = \frac{1}{2}\cdot\frac{2}{3}u^{3/2} = \frac{1}{3}(x^2+9)^{3/2} + C$.

### Example 3: trig identity, $\int \sin^2 x\,dx$

Even power: use the half-angle identity.

$\int \sin^2 x\,dx = \int \frac{1 - \cos 2x}{2} dx = \frac{x}{2} - \frac{\sin 2x}{4} + C.$

### Example 4: partial fractions, $\int \frac{dx}{x^2 - 1}$

$x^2 - 1 = (x-1)(x+1)$, so $\frac{1}{(x-1)(x+1)} = \frac{A}{x-1} + \frac{B}{x+1}$. Multiply out:
$1 = A(x+1) + B(x-1)$. Put $x = 1$: $A = \frac12$. Put $x = -1$: $B = -\frac12$.

$\int \frac{dx}{x^2-1} = \frac{1}{2}\ln\lvert x-1\rvert - \frac{1}{2}\ln\lvert x+1\rvert + C = \frac12 \ln\left\lvert\frac{x-1}{x+1}\right\rvert + C.$

## Common mistakes

- Forgetting $+C$ on indefinite integrals (exams take points for it).
- Substituting $u$ but leaving an $x$ in the integral. After substitution, only $u$ may remain.
- $\int \frac{1}{x^2}dx$ is $-\frac{1}{x}$, not $\ln(x^2)$. The $\ln$ rule is only for $\frac{1}{x}$ (or $\frac{g'}{g}$).
- $\int \sin(2x)\,dx = -\frac{1}{2}\cos(2x)$: the inner factor $2$ gives a $\frac12$.
- Choosing $u = e^x$ in $\int x e^x dx$: the integral gets harder, not easier.

## Practice

1. $\int x^2 e^{x^3}\,dx$
2. $\int x \ln x\,dx$
3. $\int \cos^2(3x)\,dx$
4. $\int e^x \sin x\,dx$ (parts twice, then solve for the integral)
5. $\int \frac{3x+1}{x^2+x}\,dx$
6. $\int \sin^3 x\,dx$

## Answers

1. $\frac{1}{3}e^{x^3} + C$ (substitution $u = x^3$).
2. $\frac{x^2}{2}\ln x - \frac{x^2}{4} + C$ ($u = \ln x$, $dv = x\,dx$).
3. $\frac{x}{2} + \frac{\sin 6x}{12} + C$.
4. $\frac{e^x(\sin x - \cos x)}{2} + C$. After two rounds of parts the original integral $I$ reappears: $I = e^x \sin x - e^x\cos x - I$.
5. $\ln\lvert x\rvert + 2\ln\lvert x+1\rvert + C$ ($A = 1$, $B = 2$).
6. $-\cos x + \frac{\cos^3 x}{3} + C$ ($\sin^3 = (1-\cos^2)\sin$, $u = \cos x$).

# Topic: Definite integrals
keywords: definite, absolute, piecewise, limits, symmetr

## Overview

A definite integral is a number: the **signed area** between the graph and the $x$-axis, area
above counting $+$, below counting $-$. The Fundamental Theorem of Calculus computes it:

$$\int_a^b f(x)\,dx = F(b) - F(a), \qquad F' = f.$$

Exams like three twists:

1. **Absolute value** $\int \lvert g(x)\rvert dx$: find the zeros of $g$, split the integral there,
   and flip the sign of every piece where $g < 0$. The result must be positive.
2. **Piecewise functions:** split the integral at every break point and use the right formula on
   each piece.
3. **Substitution with limits:** when $u = g(x)$, the limits change too: $x = a \to u = g(a)$.
   Convert them immediately and never go back to $x$.

**Symmetry shortcut:** on $[-a, a]$ an odd function ($f(-x) = -f(x)$, e.g. $x^3$, $x^5\cos x$)
integrates to $0$; an even function gives $2\int_0^a f$.

## Worked examples

### Example 1: absolute value, $\int_0^{\pi} \lvert\cos x\rvert\,dx$

$\cos x \ge 0$ on $[0, \frac{\pi}{2}]$ and $\le 0$ on $[\frac{\pi}{2}, \pi]$. Split and flip:

$\int_0^{\pi/2}\cos x\,dx + \int_{\pi/2}^{\pi}(-\cos x)\,dx = [\sin x]_0^{\pi/2} - [\sin x]_{\pi/2}^{\pi} = 1 - (0 - 1) = 2.$

Without the absolute value the answer would be $0$: the two humps cancel.

### Example 2: piecewise, $\int_0^{e} f(x)\,dx$ with $f(x) = x^2$ for $x < 1$, $f(x) = \frac{2}{x}$ for $x \ge 1$

$\int_0^1 x^2 dx + \int_1^e \frac{2}{x} dx = \left[\frac{x^3}{3}\right]_0^1 + [2\ln x]_1^e = \frac13 + 2 = \frac{7}{3}.$

### Example 3: substitution with limits, $\int_0^{\sqrt 8} x\sqrt{1+x^2}\,dx$

$u = 1 + x^2$, $du = 2x\,dx$. Limits: $x = 0 \to u = 1$, $x = \sqrt 8 \to u = 9$.

$\frac{1}{2}\int_1^9 u^{1/2}du = \frac12\cdot\frac23\left[u^{3/2}\right]_1^9 = \frac13(27 - 1) = \frac{26}{3}.$

## Common mistakes

- Integrating $\lvert g\rvert$ as $\lvert G\rvert$, or forgetting to split. Always find the zeros first.
- Keeping the old $x$-limits after a substitution.
- Sign slips in $F(b) - F(a)$ when $F(a)$ is negative: put $F(a)$ in brackets.
- Missing a break point of a piecewise function that lies inside $[a, b]$.

## Practice

1. $\int_{-2}^{2}\lvert x^2 - 1\rvert\,dx$
2. $\int_{-1}^{2} f(x)\,dx$ with $f(x) = x + 1$ for $x < 0$ and $f(x) = \frac{1}{x+1}$ for $x \ge 0$
3. $\int_1^e \frac{(\ln x)^3}{x}\,dx$
4. $\int_0^1 x e^{-x^2}\,dx$
5. $\int_0^{2\pi}\lvert\sin x\rvert\,dx$
6. $\int_{-3}^{3}\left(x^5\cos x + 2\right)dx$ (no integration needed for the first term)

## Answers

1. $4$ (even function: $2\left[\int_0^1 (1-x^2)dx + \int_1^2 (x^2-1)dx\right] = 2\left[\frac23 + \frac43\right]$).
2. $\frac12 + \ln 3$.
3. $\frac14$ ($u = \ln x$, limits $0 \to 1$).
4. $\frac12\left(1 - \frac1e\right)$ ($u = x^2$).
5. $4$.
6. $12$: $x^5\cos x$ is odd, so it contributes $0$; $\int_{-3}^3 2\,dx = 12$.

# Topic: Solids of revolution
keywords: solid, revolution, disk, disc, washer, shell

## Overview

Spin a flat region around a line (the **axis**) and you get a solid. To find its volume, cut it
into thin pieces whose volume you know, then add them up with an integral.

**Disk / washer (cut perpendicular to the axis).** Each slice is a disk of radius $R$, or a
washer with outer radius $R$ and inner radius $r$:

$$V = \pi\int_a^b \left(R^2 - r^2\right)dx.$$

**Shell (cut parallel to the axis).** Each thin strip sweeps a cylinder of radius $\rho$
(distance from the strip to the axis), height $h$ and thickness $dx$:

$$V = 2\pi\int_a^b \rho(x)\,h(x)\,dx.$$

**Radius is always a distance to the axis.** Axis $y = k$: radius $= \lvert y - k\rvert$. Axis
$x = c$: radius $= \lvert x - c\rvert$. Axis $y = -1$ adds $1$ to every height; axis $x = 2$ to the
right of the region gives $2 - x$.

**Which method?** Shells let you integrate along the variable the region is described in, even
when the axis is perpendicular to it. Region given as $y = f(x)$ and vertical axis: shells in $x$.
Horizontal axis: washers in $x$.

**Surface area** of the curved surface made by $y = f(x)$, $a \le x \le b$:

$$S = 2\pi\int_a^b \text{radius}\cdot\sqrt{1 + f'(x)^2}\,dx.$$

The **total surface of a solid** also includes flat end caps (disks or washers, area
$\pi(R^2 - r^2)$) and cylinders from straight edges parallel to the axis ($2\pi r h$). Check every
edge of the region: on the axis gives nothing, parallel to the axis gives a cylinder,
perpendicular to the axis gives a flat cap, a curve needs the integral.

**Mass:** $m = \int \rho\,dV$. Slice so that the density is constant on each slice: density
depending on height $y$ means horizontal slices.

## Worked examples

### Example 1: one region, three axes

Region $R$ between $y = x$ (top) and $y = x^2$ (bottom), $0 \le x \le 1$.

**About the $x$-axis (washers):** $R = x$, $r = x^2$.
$V = \pi\int_0^1 (x^2 - x^4)\,dx = \pi\left(\frac13 - \frac15\right) = \frac{2\pi}{15}$.

**About the $y$-axis (shells):** radius $x$, height $x - x^2$.
$V = 2\pi\int_0^1 x(x - x^2)\,dx = 2\pi\left(\frac13 - \frac14\right) = \frac{\pi}{6}$.

**About the line $x = 2$ (shells):** radius $2 - x$ (the axis is to the right).
$V = 2\pi\int_0^1 (2-x)(x-x^2)\,dx = 2\pi\int_0^1 (2x - 3x^2 + x^3)\,dx = 2\pi\left(1 - 1 + \frac14\right) = \frac{\pi}{2}$.

*Why:* same region, but the radius is the distance to whichever axis you spin around.

### Example 2: surface area, $y = \sqrt x$, $0 \le x \le 2$, about the $x$-axis

$f'(x) = \frac{1}{2\sqrt x}$, so $\sqrt x\sqrt{1 + \frac{1}{4x}} = \sqrt{x + \frac14}$.

$S = 2\pi\int_0^2\sqrt{x + \tfrac14}\,dx = \frac{4\pi}{3}\left[(x+\tfrac14)^{3/2}\right]_0^2 = \frac{4\pi}{3}\left(\frac{27}{8} - \frac18\right) = \frac{13\pi}{3}.$

*Trick worth remembering:* multiply the radius into the square root before integrating.

### Example 3: mass with height-dependent density

Rotate $y = 1 - x^2$, $0 \le x \le 1$, about the $y$-axis (a dome). Density $\rho(y) = 2 - y$.

Density depends on $y$, so slice horizontally: at height $y$ the slice is a disk of radius
$x = \sqrt{1-y}$, so $dV = \pi(1-y)\,dy$.

$m = \int_0^1 (2-y)\,\pi(1-y)\,dy = \pi\int_0^1 (2 - 3y + y^2)\,dy = \pi\left(2 - \frac32 + \frac13\right) = \frac{5\pi}{6}.$

## Common mistakes

- Using $(R - r)^2$ instead of $R^2 - r^2$ for washers.
- Forgetting the inner radius when the region does not touch the axis.
- Radius measured from the $x$-axis when the axis is $y = k$.
- Surface area with $dx$ instead of $ds = \sqrt{1 + f'^2}\,dx$.
- Total surface without the flat caps or the inner cylinder.

## Practice

1. Rotate the region under $y = \sqrt x$, $0 \le x \le 4$, about the $x$-axis. Volume?
2. Rotate the region between $y = 2x$ and $y = x^2$ about the $y$-axis. Volume (shells)?
3. Rotate the same region about the line $y = -1$. Volume (washers)?
4. Surface area of the surface made by rotating $y = x^3$, $0 \le x \le 1$, about the $x$-axis.
5. Rotate the triangle bounded by $y = x$, $y = 0$, $x = 3$ about the $x$-axis. Total surface area of the solid (a cone)?
6. The same triangle but with $0 \le x \le 2$ and density $\rho(x) = 1 + x$. Mass of the cone?

## Answers

1. $8\pi$ ($\pi\int_0^4 x\,dx$).
2. $\frac{8\pi}{3}$ ($2\pi\int_0^2 x(2x - x^2)\,dx$).
3. $\frac{104\pi}{15}$ ($R = 2x + 1$, $r = x^2 + 1$: $\pi\int_0^2 (2x^2 + 4x - x^4)\,dx$).
4. $\frac{\pi}{27}\left(10\sqrt{10} - 1\right)$ (substitute $u = 1 + 9x^4$).
5. $9\pi(1 + \sqrt 2)$: curved part $2\pi\int_0^3 x\sqrt2\,dx = 9\sqrt2\pi$, plus the base disk $9\pi$.
6. $\frac{20\pi}{3}$ ($\pi\int_0^2 (1+x)x^2\,dx$, disks perpendicular to the $x$-axis because the density depends on $x$).

# Topic: Parametric curves
keywords: parametric, cycloid

## Overview

A parametric curve gives both coordinates as functions of a parameter $t$ (think: time):
$x = x(t)$, $y = y(t)$. A point moves along the curve as $t$ grows. Every formula is the
ordinary one with $dx = x'(t)\,dt$ substituted:

| Quantity | Formula |
|---|---|
| slope | $\frac{dy}{dx} = \frac{y'(t)}{x'(t)}$ |
| area between curve and $x$-axis | $A = \int y(t)\,x'(t)\,dt$ (take the absolute value; mind the direction) |
| arc length | $L = \int \sqrt{x'(t)^2 + y'(t)^2}\,dt$ |
| surface, rotating about $y = k$ | $S = 2\pi\int \lvert y(t) - k\rvert\sqrt{x'^2 + y'^2}\,dt$ |
| surface, rotating about $x = c$ | $S = 2\pi\int \lvert x(t) - c\rvert\sqrt{x'^2 + y'^2}\,dt$ |

**Only part of the curve?** Translate the condition into $t$: "left of the $y$-axis" means
$x(t) \le 0$; solve that inequality for the $t$-interval.

**Look for perfect squares** under the root: $x'^2 + y'^2$ is often built to be $(\ldots)^2$.

## Worked examples

### Example 1: area under a cycloid arch, $x = t - \sin t$, $y = 1 - \cos t$, $0 \le t \le 2\pi$

$x'(t) = 1 - \cos t$. $A = \int_0^{2\pi}(1-\cos t)^2 dt = \int_0^{2\pi}(1 - 2\cos t + \cos^2 t)\,dt = 2\pi - 0 + \pi = 3\pi.$

### Example 2: arc length, $x = t^2$, $y = \frac{t^3}{3}$, $0 \le t \le \sqrt5$

$x' = 2t$, $y' = t^2$, $\sqrt{4t^2 + t^4} = t\sqrt{4 + t^2}$ for $t \ge 0$.

$L = \int_0^{\sqrt5} t\sqrt{4+t^2}\,dt = \frac13\left[(4+t^2)^{3/2}\right]_0^{\sqrt5} = \frac13(27 - 8) = \frac{19}{3}.$

### Example 3: area between curve and $x$-axis, $x = 3t$, $y = 4 - t^2$

$y \ge 0$ for $-2 \le t \le 2$, and $x$ increases with $t$, so no sign issue.

$A = \int_{-2}^{2}(4 - t^2)\cdot 3\,dt = 3\left[4t - \frac{t^3}{3}\right]_{-2}^{2} = 3\cdot 2\left(8 - \frac83\right) = 32.$

*Check:* eliminating $t$ gives $y = 4 - \frac{x^2}{9}$ on $[-6, 6]$, area $48 - 16 = 32$. ✓

## Common mistakes

- Integrating $y\,dt$ instead of $y\,x'(t)\,dt$.
- Wrong $t$-interval: always derive it from the condition on $x$ or $y$.
- A negative area because $x$ decreases as $t$ grows: take the absolute value (and say so).
- In the surface formula using $y(t)$ when the axis is $y = k$: the radius is $\lvert y(t) - k\rvert$.

## Practice

1. Arc length of the astroid arc $x = \cos^3 t$, $y = \sin^3 t$, $0 \le t \le \frac{\pi}{2}$.
2. Area enclosed by the ellipse $x = 3\cos t$, $y = 2\sin t$, $0 \le t \le 2\pi$.
3. Arc length of $x = e^t\cos t$, $y = e^t\sin t$, $0 \le t \le 1$.
4. Rotate $x = t^2$, $y = 2t$, $0 \le t \le 1$ about the $x$-axis. Surface area?
5. The curve $x = t^2 - 1$, $y = t^3 - t$ crosses itself at the origin. Area of its loop?
6. For $x = t^2$, $y = t^3 - 3t$: slope at $t = 2$, and the points with a horizontal tangent.

## Answers

1. $\frac32$ ($\sqrt{x'^2 + y'^2} = 3\sin t\cos t$).
2. $6\pi$ ($\lvert\int_0^{2\pi} 2\sin t\cdot(-3\sin t)\,dt\rvert$).
3. $\sqrt2(e - 1)$ ($x'^2 + y'^2 = 2e^{2t}$).
4. $\frac{8\pi}{3}\left(2\sqrt2 - 1\right)$ ($S = 2\pi\int_0^1 2t\cdot2\sqrt{t^2+1}\,dt$).
5. $\frac{8}{15}$ (loop for $-1 \le t \le 1$: $\lvert\int_{-1}^1 (t^3 - t)\,2t\,dt\rvert$).
6. Slope $\frac94$; horizontal tangent where $y'(t) = 3t^2 - 3 = 0$: points $(1, -2)$ and $(1, 2)$.

# Topic: Polar curves
keywords: polar, cardioid, limaçon, limacon, rose, inner loop

## Overview

In polar coordinates a point is given by its distance $r$ from the origin and its angle
$\theta$: $x = r\cos\theta$, $y = r\sin\theta$, $r^2 = x^2 + y^2$. A polar curve $r = f(\theta)$ is
drawn by turning a ray and marking distance $r$ on it.

**Shapes to recognise:**

| Equation | Shape |
|---|---|
| $r = a$ | circle of radius $a$ around the origin |
| $r = 2a\cos\theta$ (or $2a\sin\theta$) | circle of radius $a$ through the origin |
| $r = a(1 + \cos\theta)$ | cardioid (heart), touches the origin |
| $r = a + b\cos\theta$ with $b > a$ | limaçon **with an inner loop** |
| $r = a\cos(n\theta)$ | rose: $n$ petals if $n$ is odd, $2n$ if even |

**Area** swept by the ray between angles $\alpha$ and $\beta$ (thin pie slices of area $\frac12 r^2 d\theta$):

$$A = \frac12\int_\alpha^\beta r^2\,d\theta, \qquad A_{\text{between}} = \frac12\int_\alpha^\beta \left(r_{\text{out}}^2 - r_{\text{in}}^2\right)d\theta.$$

**Arc length:** $L = \int_\alpha^\beta \sqrt{r^2 + \left(\frac{dr}{d\theta}\right)^2}\,d\theta$.

**Inner loops:** the loop is traced while $r < 0$. Solve $r(\theta) = 0$ to get its angles. The
area "excluding the small loop" is (big loop) $-$ (small loop), because the big loop's integral
covers the small one too.

**Intersections:** solve $r_1(\theta) = r_2(\theta)$, and check the origin separately (curves can
pass through it at different angles).

## Worked examples

### Example 1: area of the cardioid $r = 1 + \cos\theta$

$A = \frac12\int_0^{2\pi}(1 + 2\cos\theta + \cos^2\theta)\,d\theta = \frac12(2\pi + 0 + \pi) = \frac{3\pi}{2}.$

### Example 2: the limaçon $r = 1 + 2\cos\theta$, inner loop and the region between the loops

$r = 0$ when $\cos\theta = -\frac12$: $\theta = \frac{2\pi}{3}, \frac{4\pi}{3}$. The inner loop is traced
for $\theta \in [\frac{2\pi}{3}, \frac{4\pi}{3}]$ (there $r < 0$), the big loop for $\theta \in [-\frac{2\pi}{3}, \frac{2\pi}{3}]$.

$r^2 = 1 + 4\cos\theta + 4\cos^2\theta = 3 + 4\cos\theta + 2\cos2\theta$, antiderivative $3\theta + 4\sin\theta + \sin2\theta$.

- Inner loop: $\frac12\left[3\theta + 4\sin\theta + \sin 2\theta\right]_{2\pi/3}^{4\pi/3} = \frac12\left(2\pi - 3\sqrt3\right) = \pi - \frac{3\sqrt3}{2} \approx 0.54$.
- Big loop: $\frac12\left[\ldots\right]_{-2\pi/3}^{2\pi/3} = 2\pi + \frac{3\sqrt3}{2}$.
- Between the loops: $\left(2\pi + \frac{3\sqrt3}{2}\right) - \left(\pi - \frac{3\sqrt3}{2}\right) = \pi + 3\sqrt3 \approx 8.34$.

### Example 3: inside $r = 3\sin\theta$ and outside $r = 1 + \sin\theta$

Intersections: $3\sin\theta = 1 + \sin\theta \Rightarrow \sin\theta = \frac12 \Rightarrow \theta = \frac{\pi}{6}, \frac{5\pi}{6}$.

$A = \frac12\int_{\pi/6}^{5\pi/6}\left(9\sin^2\theta - (1+\sin\theta)^2\right)d\theta = \frac12\int_{\pi/6}^{5\pi/6}(3 - 4\cos2\theta - 2\sin\theta)\,d\theta$

$= \frac12\left[3\theta - 2\sin2\theta + 2\cos\theta\right]_{\pi/6}^{5\pi/6} = \frac12\left(\frac{5\pi}{2} - \frac{\pi}{2}\right) = \pi.$

## Common mistakes

- Integrating $r$ instead of $\frac12 r^2$.
- Integrating the limaçon over $[0, 2\pi]$ and calling it "the area": that counts the inner loop twice.
- Wrong angle range for a petal: find where $r = 0$.
- Forgetting $\cos^2\theta = \frac{1 + \cos2\theta}{2}$ and getting stuck.

## Practice

1. Area of one petal of the rose $r = \cos3\theta$.
2. Area inside $r = 2\cos\theta$ (and confirm with geometry).
3. Arc length of the cardioid $r = 1 + \cos\theta$.
4. Area inside the circle $r = 1$ and outside the cardioid $r = 1 - \cos\theta$.
5. For $r = 1 + 2\sin\theta$: at which angles is $r = 0$, and what is the area of the inner loop?
6. Write $r = 4\sin\theta$ in Cartesian coordinates and name the curve.

## Answers

1. $\frac{\pi}{12}$ (petal for $-\frac{\pi}{6} \le \theta \le \frac{\pi}{6}$).
2. $\pi$: a circle of radius $1$.
3. $8$ ($r^2 + r'^2 = 2 + 2\cos\theta = 4\cos^2\frac\theta2$).
4. $2 - \frac{\pi}{4}$ ($\frac12\int_{-\pi/2}^{\pi/2}(2\cos\theta - \cos^2\theta)\,d\theta$).
5. $\theta = \frac{7\pi}{6}, \frac{11\pi}{6}$; inner loop $\pi - \frac{3\sqrt3}{2}$ (Example 2 turned by $90°$).
6. $x^2 + (y-2)^2 = 4$: circle with centre $(0, 2)$, radius $2$.

# Topic: Probability densities
keywords: probability, densit, expected, cdf, median, random variable

## Overview

A continuous random variable $X$ (a waiting time, a length, a deviation) is described by a
**density** $f(x)$. Probabilities are areas under $f$:

$$P(a \le X \le b) = \int_a^b f(x)\,dx.$$

A valid density needs $f(x) \ge 0$ and $\int_{-\infty}^{\infty} f(x)\,dx = 1$. That second condition
is how you find an unknown constant ("normalise").

| Quantity | Formula | Meaning |
|---|---|---|
| CDF | $F(x) = \int_{-\infty}^{x} f(t)\,dt$ | $P(X \le x)$ |
| expected value | $E[X] = \int x f(x)\,dx$ | long-run average, the balance point of $f$ |
| variance | $\operatorname{Var}X = E[X^2] - (E[X])^2$ | spread |
| median $m$ | $F(m) = \frac12$ | half the probability on each side |

Piecewise densities: split every integral at the break points. Symmetric densities: the mean
(and median) is the centre of symmetry, no integral needed.

## Worked examples

### Example 1: $f(x) = c\,x(2 - x)$ on $[0, 2]$, zero elsewhere

- **Normalise:** $\int_0^2 (2x - x^2)\,dx = 4 - \frac83 = \frac43$, so $c = \frac34$.
- **$P(X > 1.5)$:** $\frac34\left[x^2 - \frac{x^3}{3}\right]_{1.5}^{2} = \frac34\left(\frac43 - \frac98\right) = \frac34\cdot\frac{5}{24} = \frac{5}{32}$.
- **$E[X]$:** $f$ is symmetric about $x = 1$, so $E[X] = 1$. (Check: $\frac34\int_0^2(2x^2 - x^3)\,dx = \frac34\cdot\frac43 = 1$.) The median is also $1$.

### Example 2: waiting time with $f(x) = \frac12 e^{-x/2}$, $x \ge 0$ (minutes)

- CDF: $F(x) = \int_0^x \frac12 e^{-t/2}dt = 1 - e^{-x/2}$.
- $P(X > 3) = 1 - F(3) = e^{-3/2} \approx 0.22$.
- Median: $1 - e^{-m/2} = \frac12 \Rightarrow m = 2\ln 2 \approx 1.39$ min.
- $E[X] = \int_0^\infty x\cdot\frac12 e^{-x/2}dx$; parts with $u = x$, $v = -e^{-x/2}$:
  $\left[-x e^{-x/2}\right]_0^\infty + \int_0^\infty e^{-x/2}dx = 0 + 2 = 2$ min.

*Why mean $\neq$ median:* the long right tail pulls the mean up.

## Common mistakes

- Forgetting to multiply by $x$ in $E[X]$ (or by $f$ at all).
- Using one formula over the whole interval of a piecewise density.
- Answering "what does $F(x)$ mean?" with a formula. Answer in words: the probability that $X$ is at most $x$.
- A probability larger than $1$ or negative: an arithmetic error, check it.

## Practice

1. $f(x) = \frac{k}{x^2}$ on $1 \le x \le 4$. Find $k$, $P(X \le 2)$, $E[X]$ and the median.
2. $f(x) = ax$ on $[0, 1)$, $f(x) = \frac{a(3-x)}{2}$ on $[1, 3]$, zero elsewhere. Find $a$, $P(X > 2)$, $E[X]$ and the median.
3. A lifetime has density $\frac15 e^{-x/5}$, $x \ge 0$ (years). $P(X > 5)$? Median?
4. In problem 2, what does $F(1)$ mean in words, and what is its value?
5. $X$ is uniform on $[0, 6]$. Find $E[X]$ and $\operatorname{Var}X$.

## Answers

1. $k = \frac43$; $P(X \le 2) = \frac23$; $E[X] = \frac43\ln4 = \frac83\ln2 \approx 1.85$; median $\frac85$.
2. $a = \frac23$ (triangle of base 3, height $a$); $P(X > 2) = \frac16$; $E[X] = \frac29 + \frac{10}{9} = \frac43$; median $3 - \sqrt3 \approx 1.27$ (since $F(1) = \frac13 < \frac12$, solve $\frac{(3-m)^2}{6} = \frac12$).
3. $e^{-1} \approx 0.37$; median $5\ln2 \approx 3.47$ years.
4. The probability that $X \le 1$; $F(1) = \frac13$.
5. $E[X] = 3$, $E[X^2] = 12$, $\operatorname{Var}X = 3$.

# Topic: Physical applications
keywords: physical, centre of mass, center of mass, work, related rate, beam, pump

## Overview

The pattern is always the same: cut the object into small pieces, write the small quantity
for one piece ($dm$, $dW$, ...), and integrate.

**Mass and centre of mass of a rod** with density $\rho(x)$ (kg/m) on $[a, b]$:

$$m = \int_a^b \rho(x)\,dx, \qquad \bar x = \frac{1}{m}\int_a^b x\,\rho(x)\,dx.$$

A beam supported at point $s$ stays balanced only if $\bar x = s$. Otherwise it tips toward the
side of $\bar x$. Shortcut: the sign of the torque $\int_a^b (x - s)\rho(x)\,dx$ tells the direction.

**Centroid of a flat region** between $f$ (top) and $g$ (bottom), area $A$:
$\bar x = \frac1A\int x\,(f - g)\,dx$, $\bar y = \frac1A\int \frac12(f^2 - g^2)\,dx$.

**Work** $W = \int F\,dx$. Spring (Hooke): $F = kx$. **Pumping** liquid: a horizontal slice at
height $y$ has volume $A(y)\,dy$, weight $\rho g A(y)\,dy$, and must be lifted a distance
$d(y)$:

$$W = \int \rho\,g\,d(y)\,A(y)\,dy.$$

**Related rates for a vessel:** if $V(h)$ is the volume up to height $h$, then
$\frac{dV}{dh} = A(h)$, the area of the liquid surface (Fundamental Theorem). So

$$\frac{dV}{dt} = A(h)\,\frac{dh}{dt} \quad\Rightarrow\quad \frac{dh}{dt} = \frac{dV/dt}{A(h)}.$$

You never need a closed formula for $V(h)$, only the radius at the current height.

## Worked examples

### Example 1: does the beam tip? Rod on $[0, 2]$ m, $\rho(x) = 1 + x^2$ kg/m, supported at $x = 1$

$m = \int_0^2(1 + x^2)\,dx = 2 + \frac83 = \frac{14}{3}$ kg,
$\int_0^2 x(1 + x^2)\,dx = 2 + 4 = 6$, so $\bar x = \frac{6}{14/3} = \frac97 \approx 1.29$ m.

$\bar x > 1$: the beam tips toward the heavier end $x = 2$.

### Example 2: pumping a cylindrical tank

Radius $1$ m, height $3$ m, full of water ($\rho = 1000$ kg/m³, $g = 9.81$ m/s²). Pump everything
out over the top. A slice at height $y$ has volume $\pi\cdot1^2\,dy$ and is lifted $3 - y$:

$W = \int_0^3 1000\cdot9.81\cdot\pi\,(3-y)\,dy = 9810\pi\cdot\frac92 = 44\,145\pi \approx 1.39\cdot10^5$ J.

### Example 3: related rates in a cone

A cone with the tip down has radius $r = \frac h2$ at height $h$ (cm). Water flows in at
$4$ cm³/s. How fast does the level rise at $h = 6$?

$A(6) = \pi\cdot3^2 = 9\pi$, so $\frac{dh}{dt} = \frac{4}{9\pi} \approx 0.14$ cm/s.

*Check with the cone formula:* $V = \frac{\pi h^3}{12}$, $\frac{dV}{dt} = \frac{\pi h^2}{4}\frac{dh}{dt} = 9\pi\frac{dh}{dt}$. ✓ Same, but
$A(h)$ also works for vessels without a volume formula.

## Common mistakes

- Taking the lifting distance as $y$ instead of (target height $-\,y$).
- Mixing units (cm and m, kg and g). Convert first.
- Answering "what happens to the beam" with a number only. State the direction and why.
- In related rates, plugging in $h$ before differentiating.

## Practice

1. A rod on $[0, 4]$ m has density $\rho(x) = 2 + x$. Mass, centre of mass, and what happens if it is supported at its centre?
2. Centroid of the region under $y = x^2$, $0 \le x \le 1$.
3. A force of $10$ N stretches a spring $0.2$ m beyond its natural length. Work to stretch it from $0.2$ m to $0.5$ m?
4. A conical tank (tip down) is $4$ m high with top radius $2$ m and full of water. Work to pump all water to the rim?
5. A bowl is made by rotating $y = x^2$ about the $y$-axis (cm). Water is poured in at $3$ cm³/s. How fast does the level rise at depth $4$ cm?
6. A $3$ m beam on $[0, 3]$ has density $\rho(x) = 2 + \sin\frac{\pi x}{3}$ and is supported at its centre. What happens, and what is its mass?

## Answers

1. $m = 16$ kg, $\bar x = \frac{112/3}{16} = \frac73 \approx 2.33$ m. It tips toward the end $x = 4$.
2. $\left(\frac34, \frac{3}{10}\right)$.
3. $k = 50$ N/m, $W = \int_{0.2}^{0.5}50x\,dx = 5.25$ J.
4. Radius at height $y$ is $\frac y2$: $W = \rho g\frac{\pi}{4}\int_0^4 y^2(4-y)\,dy = \frac{16\pi\rho g}{3} = 52\,320\pi \approx 1.64\cdot10^5$ J.
5. $A(h) = \pi h$, so $\frac{dh}{dt} = \frac{3}{4\pi} \approx 0.24$ cm/s.
6. $\rho(3 - x) = \rho(x)$, so the density is symmetric about $1.5$: the beam stays balanced. Mass $6 + \frac{6}{\pi}$ kg.

# Topic: Double integrals over polygonal regions
keywords: double, polygon, region, type i, iterated

## Overview

A double integral $\iint_D f(x,y)\,dA$ adds up $f$ over a flat region $D$. If $f = 1$ it is the
area of $D$; if $f$ is a height it is a volume. You compute it as two ordinary integrals, one
inside the other:

- **Type I (vertical strips):** $x$ from $a$ to $b$, and for each $x$, $y$ from the bottom edge
  $g_1(x)$ to the top edge $g_2(x)$: $\int_a^b\int_{g_1(x)}^{g_2(x)} f\,dy\,dx$.
- **Type II (horizontal strips):** $y$ from $c$ to $d$, and $x$ from the left edge $h_1(y)$ to
  the right edge $h_2(y)$: $\int_c^d\int_{h_1(y)}^{h_2(y)} f\,dx\,dy$.

**Recipe for polygons:**
1. Sketch the region and mark the vertices.
2. Write every edge as a line equation, solved for $y$ (type I) or for $x$ (type II).
3. Choose the order with the **fewest pieces**: if the top (or bottom) edge changes along the
   way, that order needs a split. A region bounded by $x = y$ and $x = y + 4$ is one piece as
   type II.
4. Inner integral first, treating the outer variable as a constant. Simplify before the outer one.

## Worked examples

### Example 1: both orders, $f = xy$ over the triangle $(0,0), (2,0), (2,2)$

Type I: $0 \le x \le 2$, $0 \le y \le x$.
$\int_0^2\int_0^x xy\,dy\,dx = \int_0^2 x\cdot\frac{x^2}{2}\,dx = \frac12\cdot\frac{16}{4} = 2$.

Type II: $0 \le y \le 2$, $y \le x \le 2$.
$\int_0^2 y\int_y^2 x\,dx\,dy = \int_0^2 y\left(2 - \frac{y^2}{2}\right)dy = 4 - 2 = 2$. ✓

### Example 2: choosing the order, $f = y$ over the triangle $(0,0), (2,2), (4,0)$

Type I needs two pieces (the top edge changes at $x = 2$). Type II is one piece: the left edge
is $x = y$, the right edge $x = 4 - y$, and $0 \le y \le 2$.

$\int_0^2\int_y^{4-y} y\,dx\,dy = \int_0^2 y(4 - 2y)\,dy = \left[2y^2 - \frac{2y^3}{3}\right]_0^2 = 8 - \frac{16}{3} = \frac83.$

## Common mistakes

- Variable limits on the outer integral. Only the inner limits may depend on the outer
  variable; the outer limits are always numbers.
- An edge equation solved for the wrong variable.
- Treating the outer variable as a variable inside the inner integral.
- Splitting into pieces when the other order would need none.

## Practice

1. $\iint_D (x + y)\,dA$ over the rectangle $[0,1]\times[0,2]$.
2. $\iint_D 2x\,dA$ over the triangle $(0,0), (1,0), (0,1)$.
3. $\iint_D (x + 2y)\,dA$ over the parallelogram bounded by $y = 0$, $y = 2$, $x = y$, $x = y + 3$.
4. Area of the triangle $(0,0), (4,0), (1,3)$ as a double integral (type II).
5. $\int_0^1\int_x^1 e^{y^2}\,dy\,dx$ (reverse the order: $e^{y^2}$ has no elementary antiderivative).
6. $\iint_D y\,dA$ over the triangle of problem 4.

## Answers

1. $3$.
2. $\frac13$.
3. $27$ (inner integral $\int_y^{y+3}(x + 2y)\,dx = 9y + \frac92$).
4. $6$ (left edge $x = \frac y3$, right edge $x = 4 - y$, $0 \le y \le 3$).
5. $\frac{e-1}{2}$ (region $0 \le x \le y \le 1$: $\int_0^1\int_0^y e^{y^2}dx\,dy = \int_0^1 y e^{y^2}dy$).
6. $6$ ($\int_0^3 y\left(4 - \frac{4y}{3}\right)dy$).

# Practice exam

*Format as in the BM20A8100 exams: no calculator, the table books and one hand-written A4
formula sheet allowed. 40 points, suggested time 3 hours. Answers may contain integrals only
where the question says so.*

**1. (7 p)**
(a) Compute $\int_0^1 x^2 e^x\,dx$. (3 p)
(b) Compute $\int_0^4 \lvert x^2 - 4x + 3\rvert\,dx$. (4 p)

**2. (11 p)**
(a) The region bounded by $y = x^2$, the $x$-axis and the line $x = 2$ rotates around the line
$x = -1$. Volume of the solid? (4 p)
(b) The region bounded by $y = \sqrt x$, the $x$-axis and the line $x = 1$ rotates around the
$x$-axis. Total surface area of the solid? (4 p)
(c) For $t \ge 0$, the part of the curve $x(t) = t - \frac{t^3}{3}$, $y(t) = t^2$ that lies to the
right of the $y$-axis rotates around the $y$-axis. Surface area? (3 p)

**3. (5 p)** A $6$ m beam lies horizontally on $[0, 6]$, is supported at its centre and
released. Its density is $\rho(x) = 2 + e^{-x}$ kg/m. What happens to the beam? Justify with an
integral. Hint: $\int x e^{-x}dx = -(x+1)e^{-x} + C$.

**4. (6 p)** The lifetime $X$ (years) of a component has density $f(x) = c(4 - x^2)$ for
$0 \le x \le 2$ and $0$ otherwise.
(a) Find $c$. (1 p)
(b) Probability that the component fails within the first year? (2 p)
(c) Expected lifetime? (2 p)
(d) What does $F(1.5) = \int_0^{1.5} f(x)\,dx$ mean in practical terms? (1 p)

**5. (5 p)** Sketch the curves $r = 2 + 2\cos\theta$ and $r = 3$ (1 p) and compute the area of the
region inside the cardioid and outside the circle (4 p).

**6. (6 p)** $D$ is the trapezoid with vertices $(0,0), (4,0), (3,2), (1,2)$.
(a) Describe $D$ as a type II region (limits for $x$ in terms of $y$). (2 p)
(b) Compute $\iint_D y\,dA$. (3 p)
(c) Why would the type I order need three pieces? (1 p)

# Practice exam answers

**1(a)** Parts twice ($u = x^2$, then $u = x$): antiderivative $(x^2 - 2x + 2)e^x$.
$\left[(x^2 - 2x + 2)e^x\right]_0^1 = e - 2$.

**1(b)** $x^2 - 4x + 3 = (x-1)(x-3)$: positive on $[0,1)$ and $(3,4]$, negative on $(1,3)$. With
$F(x) = \frac{x^3}{3} - 2x^2 + 3x$: $F(0) = 0$, $F(1) = \frac43$, $F(3) = 0$, $F(4) = \frac43$.
Pieces: $\frac43 + \frac43 + \frac43 = 4$.

**2(a)** Shells: radius $x + 1$, height $x^2$. $V = 2\pi\int_0^2 (x+1)x^2\,dx = 2\pi\left(4 + \frac83\right) = \frac{40\pi}{3}$.

**2(b)** Curved part: $2\pi\int_0^1\sqrt{x + \frac14}\,dx = \frac{4\pi}{3}\left[\left(\tfrac54\right)^{3/2} - \left(\tfrac14\right)^{3/2}\right] = \frac{\pi}{6}(5\sqrt5 - 1)$.
Flat cap at $x = 1$: disk of radius $1$, area $\pi$. The edge on the $x$-axis is on the axis, so it
adds nothing. Total $S = \frac{\pi}{6}(5\sqrt5 - 1) + \pi = \frac{5\pi}{6}(\sqrt5 + 1) \approx 8.47$.

**2(c)** $x(t) = t\left(1 - \frac{t^2}{3}\right) \ge 0$ for $0 \le t \le \sqrt3$. $x' = 1 - t^2$, $y' = 2t$, and
$x'^2 + y'^2 = (1 + t^2)^2$, so $ds = (1 + t^2)\,dt$. Radius $= x(t)$:
$S = 2\pi\int_0^{\sqrt3}\left(t - \frac{t^3}{3}\right)(1 + t^2)\,dt = 2\pi\left[\frac{t^2}{2} + \frac{t^4}{6} - \frac{t^6}{18}\right]_0^{\sqrt3} = 2\pi\cdot\frac32 = 3\pi$.

**3** Torque about the support: $\int_0^6 (x - 3)(2 + e^{-x})\,dx$. The part $\int_0^6 2(x-3)\,dx = 0$
by symmetry; the rest is $\left[-(x-2)e^{-x}\right]_0^6 = -4e^{-6} - 2 < 0$. Equivalently
$m = 13 - e^{-6}$ and $\bar x = 3 - \frac{2 + 4e^{-6}}{13 - e^{-6}} < 3$. The centre of mass is left of
the support: the beam tips toward the end $x = 0$, where $e^{-x}$ makes it heavier.

**4** (a) $\int_0^2(4 - x^2)\,dx = \frac{16}{3}$, so $c = \frac{3}{16}$.
(b) $P(X \le 1) = \frac{3}{16}\left(4 - \frac13\right) = \frac{11}{16}$.
(c) $E[X] = \frac{3}{16}\int_0^2 (4x - x^3)\,dx = \frac{3}{16}(8 - 4) = \frac34$ years.
(d) The probability that the component fails within the first $1.5$ years.

**5** The cardioid reaches from $r = 0$ to $r = 4$; the circle has radius 3. Intersection:
$2 + 2\cos\theta = 3 \Rightarrow \theta = \pm\frac{\pi}{3}$.
$A = \frac12\int_{-\pi/3}^{\pi/3}\left[(2 + 2\cos\theta)^2 - 9\right]d\theta = \frac12\int_{-\pi/3}^{\pi/3}(-3 + 8\cos\theta + 2\cos2\theta)\,d\theta$
$= \frac12\left[-3\theta + 8\sin\theta + \sin2\theta\right]_{-\pi/3}^{\pi/3} = \frac{9\sqrt3}{2} - \pi \approx 4.65$.

**6** (a) $0 \le y \le 2$, left edge through $(0,0)$ and $(1,2)$: $x = \frac y2$; right edge through
$(4,0)$ and $(3,2)$: $x = 4 - \frac y2$.
(b) $\int_0^2 y\left(4 - \frac y2 - \frac y2\right)dy = \int_0^2 (4y - y^2)\,dy = 8 - \frac83 = \frac{16}{3}$.
(c) The top edge changes twice along $x$: $y = 2x$ on $[0,1]$, $y = 2$ on $[1,3]$, $y = 8 - 2x$ on $[3,4]$.
