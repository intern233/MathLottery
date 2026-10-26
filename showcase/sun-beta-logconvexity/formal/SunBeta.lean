import Mathlib.Data.Rat.Cast.Order
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Algebra.Polynomial.Coeff
import Mathlib.Algebra.BigOperators.NatAntidiagonal
import Mathlib.Data.Nat.Choose.Basic
import Mathlib.Tactic.FieldSimp
import Lean.Elab.Tactic.Omega

/- Complete original statement and proof; no external project modules. -/

/- CertificateData -/
/- Explicit polynomial certificates for the beta coefficient inequality.
   No theorem about the original sequence is assumed in this file. -/
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000

namespace SunBeta.Cert


def P (n k l : ℚ) : ℚ :=
  (n+1)*((n+l)*(n+l+1)*(n-k+1)^2*(n-k)^2 +
    (n+k)*(n+k+1)*(n-l+1)^2*(n-l)^2) -
  2*n*(n+k)*(n+l)*(n-k+1)^2*(n-l+1)^2

def A (n k l : ℚ) : ℚ := (n+k)*l^3*(n-k+1)^2

def T0 (n k l : ℚ) : ℚ :=
  (k-l+1)*A n k l - (k-l-1)*A n l k

def T1 (n k l : ℚ) : ℚ :=
  (k-l+1)*A n k l*k*(l-1) - (k-l-1)*A n l k*(k-1)*l

theorem P_symm (n k l : ℚ) : P n k l = P n l k := by unfold P; ring

theorem T0_symm (n k l : ℚ) : T0 n k l = T0 n l k := by unfold T0 A; ring

theorem T1_symm (n k l : ℚ) : T1 n k l = T1 n l k := by unfold T1 A; ring

def denEven (m r : ℚ) : ℚ := (3 * (m ^ 2) * (r ^ 2) * ((-1 + m) ^ 3) * (1 + r + (2 * m)))

def alphaEven (m r : ℚ) : ℚ := ((m * ((m * (4 + (m * (4 + (m * (-4 + (m * (-4 + (r * (4 + (r * (7 + (-25 * r))))) + (-18 * m * (r ^ 2)))) + (r * (-8 + (r * (20 + (-8 * (r ^ 2)))))))) + (r * (-10 + (r * (3 + (r * (26 + (-23 * r))))))))) + (r * (8 + (r * (-12 + (r * (26 + (r * (40 + (-12 * r))))))))))) + (r * (6 + ((r ^ 2) * (-18 + (r * (9 + (21 * r))))))))) + ((r ^ 3) * (-9 + (r * (-18 + (-9 * r))))))

def betaEven (m r : ℚ) : ℚ := ((m * (4 + (m * (8 + (m * (4 + (r * (-4 + (r * (23 + (49 * r))))) + (18 * m * (r ^ 2)))) + (r * (4 + (r * (-27 + (r * (13 + (38 * r))))))))) + (r * (14 + (r * (-12 + (r * (-40 + (r * (-11 + (9 * r))))))))))) + (r * (6 + (r * (6 + (r * (-9 + (r * (-15 + (-6 * r))))))))))

-- 334 strictly positive integer coefficients.

def posEven (u v t : ℚ) : ℚ :=
  (677376 + (t * (4817664 + (t * (15752448 + (t * (31053184 + (t * (40811488 + (t * (37423472 + (t * (24381408 + (t * (11271744 + (t * (3621472 + (t * (769904 + (t * (97472 + (5568 * t))))))))))))))))))))) + (u * (2050560 + (t * (13398912 + (t * (39701632 + (t * (69831616 + (t * (80413856 + (t * (63179256 + (t * (34244968 + (t * (12633960 + (t * (3035096 + (t * (428704 + (27040 * t))))))))))))))))))) + (u * (2575584 + (t * (15328080 + (t * (40717800 + (t * (63025020 + (t * (62424144 + (t * (40944120 + (t * (17764056 + (t * (4913532 + (t * (786144 + (55440 * t))))))))))))))))) + (u * (1740528 + (t * (9341640 + (t * (21963324 + (t * (29395494 + (t * (24421370 + (t * (12875210 + (t * (4203506 + (t * (776856 + (62232 * t))))))))))))))) + (u * (684288 + (t * (3274632 + (t * (6705660 + (t * (7578432 + (t * (5091022 + (t * (2030318 + (t * (444900 + (41328 * t))))))))))))) + (u * (156816 + (t * (659952 + (t * (1152300 + (t * (1062540 + (t * (544248 + (t * (146676 + (16248 * t))))))))))) + (u * (19440 + (t * (70704 + (t * (102156 + (t * (72776 + (t * (25480 + (3504 * t))))))))) + (u * (1008 + (t * (3096 + (t * (3536 + (t * (1760 + (320 * t))))))) + (v * (2328 + (t * (5152 + (t * (3744 + (896 * t))))) + (v * (1808 + (t * (2592 + (960 * t))) + (v * (608 + (128 * v) + (512 * t))))))))) + (v * (48240 + (t * (135384 + (t * (140600 + (t * (64104 + (10832 * t))))))) + (v * (42456 + (t * (86200 + (t * (58484 + (13200 * t))))) + (v * (17032 + (t * (23888 + (8304 * t))) + (v * (4028 + (384 * v) + (2816 * t))))))))))) + (v * (415152 + (t * (1414008 + (t * (1905876 + (t * (1271112 + (t * (419620 + (54872 * t))))))))) + (v * (406788 + (t * (1071528 + (t * (1055004 + (t * (459640 + (74700 * t))))))) + (v * (189240 + (t * (374736 + (t * (246480 + (53776 * t))))) + (v * (50592 + (t * (67132 + (22124 * t))) + (v * (7348 + (424 * v) + (4848 * t))))))))))))) + (v * (1919592 + (t * (7704432 + (t * (12775416 + (t * (11200018 + (t * (5475082 + (t * (1415234 + (151156 * t))))))))))) + (v * (2064984 + (t * (6706668 + (t * (8670731 + (t * (5575868 + (t * (1782995 + (226762 * t))))))))) + (v * (1090428 + (t * (2807684 + (t * (2701848 + (t * (1150936 + (183026 * t))))))) + (v * (328611 + (t * (635328 + (t * (407872 + (86890 * t))))) + (v * (58044 + (t * (75066 + (24142 * t))) + (v * (5469 + (204 * v) + (3548 * t))))))))))))))) + (v * (5138856 + (t * (23796936 + (t * (46921758 + (t * (51026186 + (t * (33039992 + (t * (12737090 + (t * (2707018 + (244724 * t))))))))))))) + (v * (5999028 + (t * (23242170 + (t * (37322515 + (t * (31787971 + (t * (15142831 + (t * (3825131 + (400282 * t))))))))))) + (v * (3536754 + (t * (11274760 + (t * (14319181 + (t * (9053704 + (t * (2849257 + (356984 * t))))))))) + (v * (1193973 + (t * (3035574 + (t * (2883588 + (t * (1212541 + (190376 * t))))))) + (v * (240774 + (t * (460902 + (t * (292841 + (61732 * t))))) + (v * (28131 + (t * (36268 + (11618 * t))) + (v * (1680 + (36 * v) + (1104 * t))))))))))))))))) + (v * (7947792 + (t * (41792808 + (t * (95707836 + (t * (124501854 + (t * (100546000 + (t * (51599678 + (t * (16431204 + (t * (2968484 + (232984 * t))))))))))))))) + (v * (9966972 + (t * (45015546 + (t * (86675772 + (t * (92195227 + (t * (58496188 + (t * (22136979 + (t * (4626572 + (411980 * t))))))))))))) + (v * (6473730 + (t * (24741894 + (t * (39212730 + (t * (32982215 + (t * (15526402 + (t * (3878407 + (401618 * t))))))))))) + (v * (2431020 + (t * (7698904 + (t * (9709790 + (t * (6095113 + (t * (1904130 + (236816 * t))))))))) + (v * (549313 + (t * (1393828 + (t * (1320141 + (t * (553049 + (86456 * t))))))) + (v * (73367 + (t * (141064 + (t * (89869 + (18968 * t))))) + (v * (5269 + (t * (6928 + (2254 * t))) + (v * (153 + (108 * t))))))))))))))))))) + (v * (6564720 + (t * (38703992 + (t * (101167452 + (t * (153559634 + (t * (148972494 + (t * (95720366 + (t * (40720822 + (t * (11058616 + (t * (1739728 + (120816 * t))))))))))))))))) + (v * (8759356 + (t * (45342960 + (t * (102181615 + (t * (130845045 + (t * (104092143 + (t * (52671823 + (t * (16554738 + (t * (2954992 + (229376 * t))))))))))))))) + (v * (6195772 + (t * (27758884 + (t * (53010607 + (t * (55925524 + (t * (35199519 + (t * (13217300 + (t * (2741746 + (242396 * t))))))))))))) + (v * (2568207 + (t * (9800024 + (t * (15495315 + (t * (12994632 + (t * (6096129 + (t * (1516943 + (156434 * t))))))))))) + (v * (646816 + (t * (2054942 + (t * (2596364 + (t * (1630806 + (t * (509243 + (63248 * t))))))))) + (v * (97438 + (t * (249158 + (t * (237354 + (t * (99827 + (15640 * t))))))) + (v * (8052 + (t * (15710 + (t * (10127 + (2156 * t))))) + (v * (279 + (t * (378 + (126 * t))))))))))))))))))))) + (v * (2232000 + (t * (14598720 + (t * (42968032 + (t * (74727488 + (t * (84881196 + (t * (65721420 + (t * (35105636 + (t * (12770068 + (t * (3027248 + (t * (422336 + (26336 * t))))))))))))))))))) + (v * (3135840 + (t * (18365648 + (t * (47598504 + (t * (71570876 + (t * (68762040 + (t * (43759856 + (t * (18444256 + (t * (4964956 + (t * (774616 + (53376 * t))))))))))))))))) + (v * (2384972 + (t * (12329032 + (t * (27714147 + (t * (35372215 + (t * (28033769 + (t * (14127417 + (t * (4421244 + (t * (785724 + (60720 * t))))))))))))))) + (v * (1077986 + (t * (4853531 + (t * (9299395 + (t * (9830169 + (t * (6192505 + (t * (2325128 + (t * (481906 + (42540 * t))))))))))))) + (v * (299184 + (t * (1153868 + (t * (1839630 + (t * (1552380 + (t * (731467 + (t * (182517 + (18846 * t))))))))))) + (v * (50180 + (t * (162046 + (t * (207456 + (t * (131635 + (t * (41405 + (5166 * t))))))))) + (v * (4676 + (t * (12236 + (t * (11883 + (t * (5071 + (802 * t))))))) + (v * (186 + (t * (375 + (t * (249 + (54 * t))))))))))))))))))))))

def exprEven (m r j : ℚ) : ℚ :=
  denEven m r * P (m+r+0) (m-j) (m+j+0) +
  alphaEven m r * T0 (m+r+0) (m-j) (m+j+0) +
  betaEven m r * T1 (m+r+0) (m-j) (m+j+0)

def edgeDenEven (m : ℚ) : ℚ := m^2

def edgeAlphaEven (m r : ℚ) : ℚ := ((2 * m) + (3 * r) + (3 * (r ^ 2)) + (4 * m * r))

def edgeExprEven (m r j : ℚ) : ℚ :=
  edgeDenEven m * P (m+r+0) (m-j) (m+j+0) +
  edgeAlphaEven m r * T0 (m+r+0) (m-j) (m+j+0)

def denOdd (m r : ℚ) : ℚ := (3 * (m ^ 3) * (r ^ 2) * ((-1 + m) ^ 3) * (3 + r + (2 * m)))

def alphaOdd (m r : ℚ) : ℚ := ((m * (576 + (m * (1008 + (m * ((m * (-900 + (m * (-576 + (m * (-108 + (r * (-36 + (r * (-51 + (-25 * r))))) + (-18 * m * (r ^ 2)))) + (r * (-528 + (r * (-176 + (r * (-92 + (-8 * r))))))))) + (r * (-1608 + (r * (-767 + (r * (-224 + (-85 * r))))))))) + (r * (-1080 + (r * (-1122 + (r * (-234 + (r * (-32 + (-30 * r))))))))))) + (r * (1356 + (r * (194 + (r * (-139 + (r * (89 + (48 * r))))))))))) + (r * (1608 + (r * (1292 + (r * (182 + (r * (-152 + (-42 * r))))))))))) + (r * (288 + (r * (648 + (r * (532 + (r * (188 + (24 * r))))))))))

def betaOdd (m r : ℚ) : ℚ := ((m * (576 + (m * (1008 + (m * (576 + (m * (108 + (r * (36 + (r * (75 + (49 * r))))) + (18 * m * (r ^ 2)))) + (r * (528 + (r * (146 + (r * (92 + (38 * r))))))))) + (r * (1644 + (r * (776 + (r * (99 + (r * (16 + (9 * r))))))))))) + (r * (1608 + (r * (1442 + (r * (494 + (r * (40 + (-6 * r))))))))))) + (r * (288 + (r * (576 + (r * (418 + (r * (131 + (15 * r))))))))))

-- 415 strictly positive integer coefficients.

def posOdd (u v t : ℚ) : ℚ :=
  (124720000 + (t * (566442000 + (t * (1184507700 + (t * (1519482970 + (t * (1344493322 + (t * (873451324 + (t * (430902194 + (t * (163317598 + (t * (47100188 + (t * (10006064 + (t * (1471616 + (t * (133216 + (5568 * t))))))))))))))))))))))) + (u * (278068000 + (t * (1155184600 + (t * (2210478490 + (t * (2597901992 + (t * (2106199322 + (t * (1247628114 + (t * (552967756 + (t * (182821870 + (t * (43820640 + (t * (7175568 + (t * (715200 + (32608 * t))))))))))))))))))))) + (u * (269030800 + (t * (1020522540 + (t * (1785793048 + (t * (1920498954 + (t * (1418712328 + (t * (754795952 + (t * (291768420 + (t * (80154362 + (t * (14805316 + (t * (1642840 + (82480 * t))))))))))))))))))) + (u * (148375200 + (t * (512703610 + (t * (818468842 + (t * (800686292 + (t * (531077238 + (t * (246564004 + (t * (79263404 + (t * (16794650 + (t * (2103768 + (117672 * t))))))))))))))))) + (u * (51241800 + (t * (160577390 + (t * (232369998 + (t * (203981602 + (t * (118246844 + (t * (45766116 + (t * (11374258 + (t * (1637592 + (103560 * t))))))))))))))) + (u * (11370600 + (t * (32057230 + (t * (41535296 + (t * (31942440 + (t * (15506824 + (t * (4661258 + (t * (790056 + (57576 * t))))))))))))) + (u * (1583000 + (t * (3963350 + (t * (4505990 + (t * (2923082 + (t * (1111034 + (t * (229232 + (19752 * t))))))))))) + (u * (126200 + (t * (275160 + (t * (266252 + (t * (137132 + (t * (36192 + (3824 * t))))))))) + (u * (4400 + (t * (8120 + (t * (6384 + (t * (2336 + (320 * t))))))) + (v * (7160 + (t * (10464 + (t * (5280 + (896 * t))))) + (v * (4272 + (t * (3936 + (960 * t))) + (v * (992 + (128 * v) + (512 * t))))))))) + (v * (206580 + (t * (387952 + (t * (283488 + (t * (93864 + (11728 * t))))))) + (v * (136056 + (t * (187260 + (t * (88332 + (14160 * t))))) + (v * (39368 + (t * (36768 + (8816 * t))) + (v * (6108 + (384 * v) + (2944 * t))))))))))) + (v * (2585900 + (t * (5873620 + (t * (5552524 + (t * (2694908 + (t * (663532 + (65704 * t))))))))) + (v * (1822400 + (t * (3320710 + (t * (2322062 + (t * (733812 + (87900 * t))))))) + (v * (618016 + (t * (847152 + (t * (394352 + (62080 * t))))) + (v * (114304 + (t * (105916 + (24940 * t))) + (v * (11076 + (424 * v) + (5232 * t))))))))))))) + (v * (18466840 + (t * (48695601 + (t * (55791331 + (t * (35226199 + (t * (12791049 + (t * (2508436 + (206028 * t))))))))))) + (v * (13566833 + (t * (30528519 + (t * (28149846 + (t * (13220385 + (t * (3144335 + (301462 * t))))))))) + (v * (5155368 + (t * (9343667 + (t * (6457301 + (t * (2009624 + (236802 * t))))))) + (v * (1103934 + (t * (1511439 + (t * (699220 + (109014 * t))))) + (v * (134196 + (t * (123992 + (28990 * t))) + (v * (8441 + (204 * v) + (3972 * t))))))))))))))) + (v * (82926920 + (t * (246556553 + (t * (327668999 + (t * (251215579 + (t * (119032577 + (t * (34535888 + (t * (5633384 + (395880 * t))))))))))))) + (v * (62239999 + (t * (164904983 + (t * (187082599 + (t * (115775379 + (t * (40988246 + (t * (7827904 + (627044 * t))))))))))) + (v * (25554896 + (t * (57366102 + (t * (52461048 + (t * (24344353 + (t * (5711193 + (540010 * t))))))))) + (v * (6131768 + (t * (11113480 + (t * (7655497 + (t * (2369345 + (277266 * t))))))) + (v * (871180 + (t * (1194837 + (t * (552319 + (85874 * t))))) + (v * (69977 + (t * (64815 + (15166 * t))) + (v * (2760 + (36 * v) + (1308 * t))))))))))))))))) + (v * (241438780 + (t * (793316297 + (t * (1185654254 + (t * (1053674616 + (t * (606590451 + (t * (229949345 + (t * (55577513 + (t * (7768348 + (477708 * t))))))))))))))) + (v * (183062761 + (t * (551051079 + (t * (732768576 + (t * (556437746 + (t * (259330962 + (t * (73752879 + (t * (11784931 + (812262 * t))))))))))))) + (v * (78889281 + (t * (209075018 + (t * (236033598 + (t * (144813744 + (t * (50720940 + (t * (9576338 + (758602 * t))))))))))) + (v * (20543696 + (t * (46108852 + (t * (42069888 + (t * (19448208 + (t * (4541103 + (427192 * t))))))))) + (v * (3269533 + (t * (5938599 + (t * (4094949 + (t * (1267372 + (148188 * t))))))) + (v * (307074 + (t * (422971 + (t * (196205 + (30586 * t))))) + (v * (15274 + (t * (14246 + (3358 * t))) + (v * (297 + (144 * t))))))))))))))))))) + (v * (446604420 + (t * (1602679743 + (t * (2639095100 + (t * (2631731974 + (t * (1753781529 + (t * (807241015 + (t * (254903117 + (t * (52812138 + (t * (6463820 + (353800 * t))))))))))))))))) + (v * (342308589 + (t * (1140406472 + (t * (1714117855 + (t * (1519147549 + (t * (866084762 + (t * (323670599 + (t * (76970860 + (t * (10585986 + (641356 * t))))))))))))))) + (v * (152033348 + (t * (457761225 + (t * (606433061 + (t * (457347244 + (t * (211285939 + (t * (59521511 + (t * (9423173 + (644014 * t))))))))))))) + (v * (41815548 + (t * (110472533 + (t * (124239321 + (t * (75910679 + (t * (26479750 + (t * (4980727 + (393250 * t))))))))))) + (v * (7204226 + (t * (16145753 + (t * (14723456 + (t * (6807196 + (t * (1590276 + (149704 * t))))))))) + (v * (753419 + (t * (1371374 + (t * (948850 + (t * (294826 + (34608 * t))))))) + (v * (43406 + (t * (60139 + (t * (28091 + (4410 * t))))) + (v * (1044 + (t * (981 + (234 * t))))))))))))))))))))) + (v * (478917400 + (t * (1867794570 + (t * (3351998779 + (t * (3674784609 + (t * (2741843906 + (t * (1457882405 + (t * (558033069 + (t * (150882526 + (t * (27358768 + (t * (2980456 + (147152 * t))))))))))))))))))) + (v * (375564390 + (t * (1362721166 + (t * (2257227514 + (t * (2250381025 + (t * (1490433269 + (t * (678745147 + (t * (211531575 + (t * (43231650 + (t * (5223936 + (282752 * t))))))))))))))))) + (v * (171449261 + (t * (569545994 + (t * (851017099 + (t * (748033640 + (t * (422453295 + (t * (156381543 + (t * (36865665 + (t * (5032816 + (303116 * t))))))))))))))) + (v * (49076547 + (t * (146266946 + (t * (191903040 + (t * (143516558 + (t * (65866057 + (t * (18468753 + (t * (2915465 + (198974 * t))))))))))))) + (v * (8931698 + (t * (23316748 + (t * (26007210 + (t * (15817513 + (t * (5509405 + (t * (1037208 + (82094 * t))))))))))) + (v * (1002956 + (t * (2226580 + (t * (2023333 + (t * (936515 + (t * (219712 + (20806 * t))))))))) + (v * (63241 + (t * (114768 + (t * (79716 + (t * (24964 + (2958 * t))))))) + (v * (1707 + (t * (2388 + (t * (1131 + (180 * t))))))))))))))))))))))) + (v * (226374000 + (t * (958879800 + (t * (1869094845 + (t * (2231041691 + (t * (1827174184 + (t * (1085373695 + (t * (478683985 + (t * (156499484 + (t * (36959980 + (t * (5957576 + (t * (585088 + (26336 * t))))))))))))))))))))) + (v * (185042700 + (t * (726708435 + (t * (1308538027 + (t * (1432788254 + (t * (1062594894 + (t * (559323407 + (t * (211426699 + (t * (56423154 + (t * (10107748 + (t * (1089896 + (53376 * t))))))))))))))))))) + (v * (87977490 + (t * (316943866 + (t * (519559343 + (t * (511393623 + (t * (334054493 + (t * (150133282 + (t * (46263156 + (t * (9373066 + (t * (1125836 + (60720 * t))))))))))))))))) + (v * (26371830 + (t * (85896207 + (t * (125804110 + (t * (108571233 + (t * (60404999 + (t * (22123780 + (t * (5183139 + (t * (705908 + (42540 * t))))))))))))))) + (v * (5071020 + (t * (14663488 + (t * (18748857 + (t * (13754255 + (t * (6237910 + (t * (1740417 + (t * (274901 + (18846 * t))))))))))))) + (v * (608240 + (t * (1526061 + (t * (1654141 + (t * (989564 + (t * (342765 + (t * (64717 + (5166 * t))))))))))) + (v * (41490 + (t * (87646 + (t * (77395 + (t * (35475 + (t * (8359 + (802 * t))))))))) + (v * (1230 + (t * (2097 + (t * (1422 + (t * (447 + (54 * t))))))))))))))))))))))))

def exprOdd (m r j : ℚ) : ℚ :=
  denOdd m r * P (m+r+1) (m-j) (m+j+1) +
  alphaOdd m r * T0 (m+r+1) (m-j) (m+j+1) +
  betaOdd m r * T1 (m+r+1) (m-j) (m+j+1)

def edgeDenOdd (m : ℚ) : ℚ := m^3

def edgeAlphaOdd (m r : ℚ) : ℚ := (-8 + (-10 * r) + (-3 * (r ^ 2)) + (-2 * m) + (4 * (m ^ 2)) + (3 * m * (r ^ 2)) + (4 * m * r) + (4 * r * (m ^ 2)))

def edgeExprOdd (m r j : ℚ) : ℚ :=
  edgeDenOdd m * P (m+r+1) (m-j) (m+j+1) +
  edgeAlphaOdd m r * T0 (m+r+1) (m-j) (m+j+1)

end SunBeta.Cert

/- CertificateEven -/
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace SunBeta.Cert

theorem posEven_nonneg (u v t : ℚ) (hu : 0 ≤ u) (hv : 0 ≤ v) (ht : 0 ≤ t) :
    0 ≤ posEven u v t := by
  unfold posEven
  positivity

theorem identityEven (u v t : ℚ) :
    exprEven (t+2+u) (t+1+v) (t+2) =
    2*((t+2)^2*((t+2)^2-1))*posEven u v t := by
  unfold exprEven denEven alphaEven betaEven P T0 T1 A posEven
  ring

theorem exprEven_0 (m r : ℚ) : exprEven m r 0 = 0 := by
  unfold exprEven denEven alphaEven betaEven P T0 T1 A
  ring

theorem exprEven_1 (m r : ℚ) : exprEven m r 1 = 0 := by
  unfold exprEven denEven alphaEven betaEven P T0 T1 A
  ring

theorem exprEven_nonneg (m r j : ℚ) (hj : 2 ≤ j)
    (hm : j ≤ m) (hr : j ≤ r+1) : 0 ≤ exprEven m r j := by
  have he := identityEven (m-j) (r+1-j) (j-2)
  have hp := posEven_nonneg (m-j) (r+1-j) (j-2) (by linarith) (by linarith) (by linarith)
  have hf : 0 ≤ (j-2+2)^2*((j-2+2)^2-1) := by
    apply mul_nonneg (sq_nonneg _)
    nlinarith [sq_nonneg (j-1)]
  have hnon : 0 ≤ exprEven (j-2+2+(m-j)) (j-2+1+(r+1-j)) (j-2+2) := by
    rw [he]
    exact mul_nonneg (mul_nonneg (by norm_num) hf) hp
  convert hnon using 1 <;> congr 1 <;> ring

theorem edgeExprEven_0 (m r : ℚ) : edgeExprEven m r 0 = 0 := by
  unfold edgeExprEven edgeDenEven edgeAlphaEven P T0 A
  ring

theorem edgeExprEven_small (r : ℚ) : edgeExprEven 1 r 1 = (2 * ((2 + r) ^ 2) * (1 + r) * (4 + (-3 * r) + (3 * (r ^ 2)))) := by
  unfold edgeExprEven edgeDenEven edgeAlphaEven P T0 A
  ring

theorem edgeExprEven_top (m : ℚ) : edgeExprEven m 0 1 = (8 * m * ((1 + m) ^ 2)) := by
  unfold edgeExprEven edgeDenEven edgeAlphaEven P T0 A
  ring

end SunBeta.Cert

/- CertificateOdd -/
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace SunBeta.Cert

theorem posOdd_nonneg (u v t : ℚ) (hu : 0 ≤ u) (hv : 0 ≤ v) (ht : 0 ≤ t) :
    0 ≤ posOdd u v t := by
  unfold posOdd
  positivity

theorem identityOdd (u v t : ℚ) :
    exprOdd (t+2+u) (t+1+v) (t+2) =
    2*((t+2)*(t+1)*(t+3)*(t+4))*posOdd u v t := by
  unfold exprOdd denOdd alphaOdd betaOdd P T0 T1 A posOdd
  ring

theorem exprOdd_0 (m r : ℚ) : exprOdd m r 0 = 0 := by
  unfold exprOdd denOdd alphaOdd betaOdd P T0 T1 A
  ring

theorem exprOdd_1 (m r : ℚ) : exprOdd m r 1 = 0 := by
  unfold exprOdd denOdd alphaOdd betaOdd P T0 T1 A
  ring

theorem exprOdd_nonneg (m r j : ℚ) (hj : 2 ≤ j)
    (hm : j ≤ m) (hr : j ≤ r+1) : 0 ≤ exprOdd m r j := by
  have he := identityOdd (m-j) (r+1-j) (j-2)
  have hp := posOdd_nonneg (m-j) (r+1-j) (j-2) (by linarith) (by linarith) (by linarith)
  have hf : 0 ≤ (j-2+2)*(j-2+1)*(j-2+3)*(j-2+4) := by
    apply mul_nonneg
    · apply mul_nonneg
      · apply mul_nonneg <;> linarith
      · linarith
    · linarith
  have hnon : 0 ≤ exprOdd (j-2+2+(m-j)) (j-2+1+(r+1-j)) (j-2+2) := by
    rw [he]
    exact mul_nonneg (mul_nonneg (by norm_num) hf) hp
  convert hnon using 1 <;> congr 1 <;> ring

theorem edgeExprOdd_0 (m r : ℚ) : edgeExprOdd m r 0 = 0 := by
  unfold edgeExprOdd edgeDenOdd edgeAlphaOdd P T0 A
  ring

theorem edgeExprOdd_small (r : ℚ) : edgeExprOdd 1 r 1 = (36 * ((3 + r) ^ 2) * (2 + r) * (14 + (2 * (r ^ 2)) + (9 * r))) := by
  unfold edgeExprOdd edgeDenOdd edgeAlphaOdd P T0 A
  ring

theorem edgeExprOdd_top (m : ℚ) : edgeExprOdd m 0 1 = (144 * m * ((2 + m) ^ 2) * (4 + (3 * m))) := by
  unfold edgeExprOdd edgeDenOdd edgeAlphaOdd P T0 A
  ring

end SunBeta.Cert

/- Basic -/
set_option maxRecDepth 4096
set_option maxHeartbeats 1000000

namespace SunBeta
open scoped BigOperators

noncomputable def beta (n : ℕ) : Polynomial ℤ :=
  ∑ k ∈ Finset.range (n+1),
    Polynomial.monomial k ((n.choose k : ℤ)^2 * ((n+k).choose k : ℤ))

def a (n k : ℕ) : ℚ := (n.choose k : ℚ)^2 * ((n+k).choose k : ℚ)

theorem a_nonneg (n k : ℕ) : 0 ≤ a n k := by unfold a; positivity

theorem a_zero {n k : ℕ} (h : n < k) : a n k = 0 := by
  simp [a, Nat.choose_eq_zero_of_lt h]

theorem choose_row (n k : ℕ) :
    ((n+1).choose k : ℚ) * ((n:ℚ)+1-k) = (n.choose k : ℚ)*((n:ℚ)+1) := by
  by_cases hk : k ≤ n+1
  · have h := congrArg (fun z : ℕ => (z : ℚ)) (Nat.choose_mul_succ_eq n k)
    push_cast [Nat.cast_sub hk] at h
    exact h.symm
  · have h1 : n+1 < k := by omega
    have h0 : n < k := by omega
    simp [Nat.choose_eq_zero_of_lt h1, Nat.choose_eq_zero_of_lt h0]

theorem choose_col (n k : ℕ) :
    (n.choose (k+1) : ℚ)*((k:ℚ)+1) = (n.choose k : ℚ)*((n:ℚ)-k) := by
  by_cases hk : k ≤ n
  · have h := congrArg (fun z : ℕ => (z : ℚ)) (Nat.choose_succ_right_eq n k)
    push_cast [Nat.cast_sub hk] at h
    exact h
  · have h0 : n < k := by omega
    have h1 : n < k+1 := by omega
    simp [Nat.choose_eq_zero_of_lt h0, Nat.choose_eq_zero_of_lt h1]

theorem choose_rising (n k : ℕ) :
    ((n+k+1).choose k : ℚ)*((n:ℚ)+1) =
    ((n+k).choose k : ℚ)*((n:ℚ)+k+1) := by
  have h := choose_row (n+k) k
  push_cast at h
  convert h using 1 <;> ring

theorem a_row (n k : ℕ) :
    a (n+1) k * ((n:ℚ)+1-k)^2 =
    ((n:ℚ)+1)*((n:ℚ)+k+1)*a n k := by
  have h1 := choose_row n k
  have h2 := choose_rising n k
  have he : n+1+k = n+k+1 := by omega
  unfold a
  rw [he]
  calc
    ((n+1).choose k : ℚ)^2 * ((n+k+1).choose k : ℚ) * ((n:ℚ)+1-k)^2 =
        (((n+1).choose k : ℚ)*((n:ℚ)+1-k))^2 * ((n+k+1).choose k : ℚ) := by ring
    _ = ((n.choose k : ℚ)*((n:ℚ)+1))^2 * ((n+k+1).choose k : ℚ) := by rw [h1]
    _ = (n.choose k : ℚ)^2*((n:ℚ)+1)*(((n+k+1).choose k : ℚ)*((n:ℚ)+1)) := by ring
    _ = _ := by rw [h2]; ring

theorem a_col (n k : ℕ) :
    a n (k+1) * ((k:ℚ)+1)^3 =
    a n k*((n:ℚ)-k)^2*((n:ℚ)+k+1) := by
  have h1 := choose_col n k
  have h2 := congrArg (fun z : ℕ => (z : ℚ)) (Nat.add_one_mul_choose_eq (n+k) k)
  push_cast at h2
  have he : n+(k+1) = n+k+1 := by omega
  unfold a
  rw [he]
  calc
    (n.choose (k+1) : ℚ)^2 * ((n+k+1).choose (k+1) : ℚ) * ((k:ℚ)+1)^3 =
      ((n.choose (k+1) : ℚ)*((k:ℚ)+1))^2 *
        (((n+k+1).choose (k+1) : ℚ)*((k:ℚ)+1)) := by ring
    _ = ((n.choose k : ℚ)*((n:ℚ)-k))^2 *
        (((n:ℚ)+k+1)*((n+k).choose k : ℚ)) := by rw [h1, ← h2]
    _ = _ := by ring

def w (n k : ℕ) : ℚ :=
  a (n+1) k / (((n:ℚ)+1)*((n:ℚ)+k)*((n:ℚ)+k+1))

theorem w_nonneg (n k : ℕ) : 0 ≤ w n k := by
  unfold w
  exact div_nonneg (a_nonneg _ _) (by positivity)

theorem w_zero {n k : ℕ} (h : n+1 < k) : w n k = 0 := by
  simp [w, a_zero h]

theorem w_above (n k : ℕ) (hn : 1 ≤ n) :
    a (n+1) k = w n k*((n:ℚ)+1)*((n:ℚ)+k)*((n:ℚ)+k+1) := by
  have hn' : (0:ℚ) < n := by exact_mod_cast (show 0 < n by omega)
  unfold w
  field_simp
  <;> ring

theorem w_center (n k : ℕ) (hn : 1 ≤ n) :
    a n k = w n k*((n:ℚ)+k)*((n:ℚ)-k+1)^2 := by
  have hn' : (0:ℚ) < n := by exact_mod_cast (show 0 < n by omega)
  have h := a_row n k
  unfold w
  field_simp
  nlinarith [h]

theorem w_below (s k : ℕ) :
    ((s:ℚ)+1)*a s k =
    w (s+1) k*((s:ℚ)+1-k+1)^2*((s:ℚ)+1-k)^2 := by
  have hc := w_center (s+1) k (by omega)
  have h := a_row s k
  push_cast at hc
  rw [hc] at h
  have hn : (0:ℚ) < (s:ℚ)+k+1 := by positivity
  apply (mul_right_cancel₀ (ne_of_gt hn))
  nlinarith [h]

theorem w_recur (n k : ℕ) (hn : 1 ≤ n) :
    w n (k+1)*((k:ℚ)+1)^3 = w n k*((n:ℚ)+k)*((n:ℚ)-k+1)^2 := by
  have hn' : (0:ℚ) < n := by exact_mod_cast (show 0 < n by omega)
  have h := a_col (n+1) k
  push_cast at h
  unfold w
  push_cast
  field_simp
  nlinarith [h]

end SunBeta

/- Sign -/
set_option maxRecDepth 8192
set_option maxHeartbeats 2000000

namespace SunBeta.Cert

def Q (n k l D a b : ℚ) : ℚ := D*P n k l + a*T0 n k l + b*T1 n k l

theorem Q_symm (n k l D a b : ℚ) : Q n k l D a b = Q n l k D a b := by
  unfold Q
  rw [P_symm n k l, T0_symm n k l, T1_symm n k l]

theorem sorted_suffices (n d : ℕ) (D a b : ℚ)
    (h : ∀ k l : ℕ, k+l=d → k≤n+1 → l≤n+1 → k≤l → 0≤Q n k l D a b) :
    ∀ k l : ℕ, k+l=d → k≤n+1 → l≤n+1 → 0≤Q n k l D a b := by
  intro k l hkl hk hl
  rcases le_total k l with hs | hs
  · exact h k l hkl hk hl hs
  · rw [Q_symm]
    exact h l k (by omega) hl hk hs

theorem even_internal (m r j : ℕ) (_hm : 2≤m) (_hr : 1≤r)
    (hj : j≤m) (hj' : j≤r+1) : 0≤exprEven m r j := by
  by_cases h0 : j=0
  · subst j; rw [Nat.cast_zero, exprEven_0]
  by_cases h1 : j=1
  · subst j; rw [Nat.cast_one, exprEven_1]
  apply exprEven_nonneg
  · exact_mod_cast (show 2≤j by omega)
  · exact_mod_cast hj
  · exact_mod_cast hj'

theorem odd_internal (m r j : ℕ) (_hm : 2≤m) (_hr : 1≤r)
    (hj : j≤m) (hj' : j≤r+1) : 0≤exprOdd m r j := by
  by_cases h0 : j=0
  · subst j; rw [Nat.cast_zero, exprOdd_0]
  by_cases h1 : j=1
  · subst j; rw [Nat.cast_one, exprOdd_1]
  apply exprOdd_nonneg
  · exact_mod_cast (show 2≤j by omega)
  · exact_mod_cast hj
  · exact_mod_cast hj'

theorem even_edge (m r j : ℕ) (hm : 1≤m) (he : m=1 ∨ r=0)
    (hj : j≤m) (hj' : j≤r+1) : 0≤edgeExprEven m r j := by
  have jj : j=0 ∨ j=1 := by rcases he with h|h <;> omega
  rcases jj with h|h
  · subst j; rw [Nat.cast_zero, edgeExprEven_0]
  subst j
  rcases he with h|h
  · subst m
    rw [Nat.cast_one, edgeExprEven_small]
    have hpoly : (0:ℚ) ≤ 4+(-3*(r:ℚ))+(3*(r:ℚ)^2) := by nlinarith [sq_nonneg (2*(r:ℚ)-1)]
    positivity
  · subst r
    rw [Nat.cast_zero, Nat.cast_one, edgeExprEven_top]
    positivity

theorem odd_edge (m r j : ℕ) (hm : 1≤m) (he : m=1 ∨ r=0)
    (hj : j≤m) (hj' : j≤r+1) : 0≤edgeExprOdd m r j := by
  have jj : j=0 ∨ j=1 := by rcases he with h|h <;> omega
  rcases jj with h|h
  · subst j; rw [Nat.cast_zero, edgeExprOdd_0]
  subst j
  rcases he with h|h
  · subst m
    rw [Nat.cast_one, edgeExprOdd_small]
    positivity
  · subst r
    rw [Nat.cast_zero, Nat.cast_one, edgeExprOdd_top]
    positivity

theorem certificate_even (m r : ℕ) :
    ∃ D a b : ℚ, 0<D ∧ ∀ k l : ℕ,
      k+l=2*m → k≤m+r+1 → l≤m+r+1 → 0≤Q ((m+r:ℕ):ℚ) k l D a b := by
  by_cases h0 : m=0
  · subst m
    refine ⟨1,0,0,by norm_num,?_⟩
    intro k l hkl hk hl
    have hk0 : k=0 := by omega
    have hl0 : l=0 := by omega
    subst k; subst l
    have he : P (r:ℚ) 0 0 = 0 := by unfold P; ring
    simpa only [Q, Nat.cast_zero, zero_add, one_mul, zero_mul, add_zero, he] using (le_refl (0:ℚ))
  have hm : 1≤m := by omega
  by_cases he : m=1 ∨ r=0
  · refine ⟨edgeDenEven m, edgeAlphaEven m r, 0, ?_, ?_⟩
    · unfold edgeDenEven
      have : (0:ℚ)<m := by exact_mod_cast (show 0<m by omega)
      positivity
    apply sorted_suffices (m+r) (2*m)
    intro k l hkl hk hl hs
    let j := m-k
    have hm' : k≤m := by omega
    have hkj : k+j=m := by dsimp [j]; omega
    have hlj : l=m+j := by omega
    have hj : j≤m := by omega
    have hj' : j≤r+1 := by omega
    have hkq : (k:ℚ)=(m:ℚ)-j := by
      have h : (k:ℚ)+(j:ℚ)=m := by exact_mod_cast hkj
      linarith
    have hlq : (l:ℚ)=(m:ℚ)+j := by exact_mod_cast hlj
    have h := even_edge m r j hm he hj hj'
    simpa only [Q, edgeExprEven, Nat.cast_add, Nat.cast_one, hkq, hlq,
      add_zero, zero_mul] using h
  · have hm2 : 2≤m := by omega
    have hr : 1≤r := by omega
    refine ⟨denEven m r, alphaEven m r, betaEven m r, ?_, ?_⟩
    · unfold denEven
      have : (1:ℚ)<m := by exact_mod_cast (show 1<m by omega)
      have : (0:ℚ)<r := by exact_mod_cast (show 0<r by omega)
      have hdiff : (0:ℚ)< -1+(m:ℚ) := by linarith
      positivity
    apply sorted_suffices (m+r) (2*m)
    intro k l hkl hk hl hs
    let j := m-k
    have hm' : k≤m := by omega
    have hkj : k+j=m := by dsimp [j]; omega
    have hlj : l=m+j := by omega
    have hj : j≤m := by omega
    have hj' : j≤r+1 := by omega
    have hkq : (k:ℚ)=(m:ℚ)-j := by
      have h : (k:ℚ)+(j:ℚ)=m := by exact_mod_cast hkj
      linarith
    have hlq : (l:ℚ)=(m:ℚ)+j := by exact_mod_cast hlj
    have h := even_internal m r j hm2 hr hj hj'
    simpa only [Q, exprEven, Nat.cast_add, Nat.cast_one, hkq, hlq, add_zero] using h

theorem certificate_odd (m r : ℕ) :
    ∃ D a b : ℚ, 0<D ∧ ∀ k l : ℕ,
      k+l=2*m+1 → k≤m+r+1+1 → l≤m+r+1+1 → 0≤Q ((m+r+1:ℕ):ℚ) k l D a b := by
  by_cases h0 : m=0
  · subst m
    refine ⟨1,0,0,by norm_num,?_⟩
    apply sorted_suffices (0+r+1) (2*0+1)
    intro k l hkl hk hl hs
    have hk0 : k=0 := by omega
    have hl1 : l=1 := by omega
    subst k; subst l
    have he : P ((r:ℚ)+1) 0 1 = 2*((r:ℚ)+1)^2*((r:ℚ)+2)^2*(3*r+4) := by unfold P; ring
    simp only [Q, zero_add, Nat.cast_add, Nat.cast_one, Nat.cast_zero, one_mul, zero_mul, add_zero]
    rw [he]
    positivity
  have hm : 1≤m := by omega
  by_cases he : m=1 ∨ r=0
  · refine ⟨edgeDenOdd m, edgeAlphaOdd m r, 0, ?_, ?_⟩
    · unfold edgeDenOdd
      have : (0:ℚ)<m := by exact_mod_cast (show 0<m by omega)
      positivity
    apply sorted_suffices (m+r+1) (2*m+1)
    intro k l hkl hk hl hs
    let j := m-k
    have hm' : k≤m := by omega
    have hkj : k+j=m := by dsimp [j]; omega
    have hlj : l=m+j+1 := by omega
    have hj : j≤m := by omega
    have hj' : j≤r+1 := by omega
    have hkq : (k:ℚ)=(m:ℚ)-j := by
      have h : (k:ℚ)+(j:ℚ)=m := by exact_mod_cast hkj
      linarith
    have hlq : (l:ℚ)=(m:ℚ)+j+1 := by exact_mod_cast hlj
    have h := odd_edge m r j hm he hj hj'
    simpa only [Q, edgeExprOdd, Nat.cast_add, Nat.cast_one, hkq, hlq,
      add_zero, zero_mul] using h
  · have hm2 : 2≤m := by omega
    have hr : 1≤r := by omega
    refine ⟨denOdd m r, alphaOdd m r, betaOdd m r, ?_, ?_⟩
    · unfold denOdd
      have : (1:ℚ)<m := by exact_mod_cast (show 1<m by omega)
      have : (0:ℚ)<r := by exact_mod_cast (show 0<r by omega)
      have hdiff : (0:ℚ)< -1+(m:ℚ) := by linarith
      positivity
    apply sorted_suffices (m+r+1) (2*m+1)
    intro k l hkl hk hl hs
    let j := m-k
    have hm' : k≤m := by omega
    have hkj : k+j=m := by dsimp [j]; omega
    have hlj : l=m+j+1 := by omega
    have hj : j≤m := by omega
    have hj' : j≤r+1 := by omega
    have hkq : (k:ℚ)=(m:ℚ)-j := by
      have h : (k:ℚ)+(j:ℚ)=m := by exact_mod_cast hkj
      linarith
    have hlq : (l:ℚ)=(m:ℚ)+j+1 := by exact_mod_cast hlj
    have h := odd_internal m r j hm2 hr hj hj'
    simpa only [Q, exprOdd, Nat.cast_add, Nat.cast_one, hkq, hlq] using h

theorem exists_certificate (n d : ℕ) (hd : d≤2*n) :
    ∃ D a b : ℚ, 0<D ∧ ∀ k l : ℕ,
      k+l=d → k≤n+1 → l≤n+1 → 0≤Q n k l D a b := by
  have hpar : d=2*(d/2) ∨ d=2*(d/2)+1 := by omega
  rcases hpar with he|ho
  · have hn : n=d/2+(n-d/2) := by omega
    rw [he, hn]
    exact certificate_even (d/2) (n-d/2)
  · have hn : n=d/2+(n-d/2-1)+1 := by omega
    rw [ho, hn]
    exact certificate_odd (d/2) (n-d/2-1)

end SunBeta.Cert

/- Convolution -/
set_option maxRecDepth 4096
set_option maxHeartbeats 2000000

namespace SunBeta
open scoped BigOperators
open Cert

-- The flux vanishes at both ends of each finite antidiagonal.
def flux (u : ℕ → ℚ) (c0 c1 : ℚ) (k l : ℕ) : ℚ :=
  u k*u l*(k:ℚ)^3*(l:ℚ)^3*((k:ℚ)-l)*
    (c0+c1*((k:ℚ)-1)*((l:ℚ)-1))

theorem flux_sum (u : ℕ → ℚ) (c0 c1 : ℚ) (d : ℕ) :
    (∑ p ∈ Finset.antidiagonal d,
      (flux u c0 c1 (p.1+1) p.2 - flux u c0 c1 p.1 (p.2+1))) = 0 := by
  have h0 := Finset.Nat.sum_antidiagonal_succ
    (n:=d) (f:=fun p => flux u c0 c1 p.1 p.2)
  have h1 := Finset.Nat.sum_antidiagonal_succ'
    (n:=d) (f:=fun p => flux u c0 c1 p.1 p.2)
  have e0 : flux u c0 c1 0 (d+1) = 0 := by simp [flux]
  have e1 : flux u c0 c1 (d+1) 0 = 0 := by simp [flux]
  simp only [e0, e1, zero_add] at h0 h1
  rw [Finset.sum_sub_distrib]
  exact sub_eq_zero.mpr (h0.symm.trans h1)

theorem weighted_flux (n k l : ℕ) (hn : 1≤n) (c0 c1 : ℚ) :
    w n k*w n l*(c0*T0 n k l+c1*T1 n k l) =
      flux (w n) c0 c1 (k+1) l - flux (w n) c0 c1 k (l+1) := by
  calc
    w n k*w n l*(c0*T0 n k l+c1*T1 n k l) =
      (w n k*((n:ℚ)+k)*((n:ℚ)-k+1)^2)*w n l*(l:ℚ)^3*
        ((k:ℚ)-l+1)*(c0+c1*(k:ℚ)*((l:ℚ)-1)) -
      w n k*(k:ℚ)^3*(w n l*((n:ℚ)+l)*((n:ℚ)-l+1)^2)*
        ((k:ℚ)-l-1)*(c0+c1*((k:ℚ)-1)*(l:ℚ)) := by
          unfold T0 T1 A
          ring
    _ = _ := by
      rw [← w_recur n k hn, ← w_recur n l hn]
      unfold flux
      push_cast
      ring

theorem weighted_telescopes (n d : ℕ) (hn : 1≤n) (c0 c1 : ℚ) :
    (∑ p ∈ Finset.antidiagonal d,
      w n p.1*w n p.2*(c0*T0 n p.1 p.2+c1*T1 n p.1 p.2)) = 0 := by
  simp_rw [weighted_flux n _ _ hn]
  exact flux_sum (w n) c0 c1 d

theorem paired_term (s k l : ℕ) :
    ((s:ℚ)+1)*(a s k*a (s+2) l+a (s+2) k*a s l-
      2*a (s+1) k*a (s+1) l) =
    w (s+1) k*w (s+1) l*P ((s:ℚ)+1) k l := by
  have hk0 := w_below s k
  have hl0 := w_below s l
  have hk1 := w_center (s+1) k (by omega)
  have hl1 := w_center (s+1) l (by omega)
  have hk2 := w_above (s+1) k (by omega)
  have hl2 := w_above (s+1) l (by omega)
  simp only [Nat.cast_add, Nat.cast_one] at hk1 hl1 hk2 hl2
  have es : s+1+1=s+2 := by omega
  rw [es] at hk2 hl2
  calc
    ((s:ℚ)+1)*(a s k*a (s+2) l+a (s+2) k*a s l-
      2*a (s+1) k*a (s+1) l) =
      (((s:ℚ)+1)*a s k)*a (s+2) l +
      a (s+2) k*(((s:ℚ)+1)*a s l) -
      2*((s:ℚ)+1)*a (s+1) k*a (s+1) l := by ring
    _ = _ := by rw [hk0,hl0,hk1,hl1,hk2,hl2]; unfold P; ring

def delta (s d : ℕ) : ℚ :=
  ∑ p ∈ Finset.antidiagonal d,
    (a s p.1*a (s+2) p.2-a (s+1) p.1*a (s+1) p.2)

theorem delta_sum (s d : ℕ) :
    2*((s:ℚ)+1)*delta s d =
      ∑ p ∈ Finset.antidiagonal d, w (s+1) p.1*w (s+1) p.2*P ((s:ℚ)+1) p.1 p.2 := by
  have hswap : (∑ p ∈ Finset.antidiagonal d, a (s+2) p.1*a s p.2) =
      ∑ p ∈ Finset.antidiagonal d, a s p.1*a (s+2) p.2 := by
    simpa only [Prod.swap, mul_comm] using
      (Finset.Nat.sum_antidiagonal_swap (n:=d) (f:=fun p => a s p.1*a (s+2) p.2))
  rw [show (∑ p ∈ Finset.antidiagonal d, w (s+1) p.1*w (s+1) p.2*P ((s:ℚ)+1) p.1 p.2) =
      ∑ p ∈ Finset.antidiagonal d, ((s:ℚ)+1)*(a s p.1*a (s+2) p.2+
        a (s+2) p.1*a s p.2-2*a (s+1) p.1*a (s+1) p.2) from
          Finset.sum_congr rfl (fun p hp => (paired_term s p.1 p.2).symm)]
  unfold delta
  simp only [Finset.sum_add_distrib, Finset.sum_sub_distrib, ← Finset.mul_sum,
    mul_assoc]
  rw [hswap]
  ring

theorem beta_coeff (n k : ℕ) :
    (beta n).coeff k = (n.choose k : ℤ)^2*((n+k).choose k : ℤ) := by
  unfold beta
  rw [Polynomial.finsetSum_coeff]
  simp only [Polynomial.coeff_monomial]
  by_cases hk : k<n+1
  · rw [Finset.sum_eq_single k]
    · simp
    · intro b hb hbk; simp [hbk]
    · simp [Finset.mem_range, hk]
  · have hz : n<k := by omega
    have hn : (n.choose k : ℤ)=0 := by simp [Nat.choose_eq_zero_of_lt hz]
    rw [hn]
    simp only [zero_pow (by decide : 2≠0), zero_mul]
    apply Finset.sum_eq_zero
    intro b hb
    have hbk : b≠k := by have := Finset.mem_range.mp hb; omega
    simp [hbk]

theorem delta_coeff (s d : ℕ) :
    (((beta s*beta (s+2)-beta (s+1)^2).coeff d : ℤ) : ℚ) = delta s d := by
  rw [Polynomial.coeff_sub, pow_two, Polynomial.coeff_mul, Polynomial.coeff_mul]
  simp_rw [beta_coeff]
  unfold delta a
  push_cast
  rw [Finset.sum_sub_distrib]

end SunBeta

/- Beta -/
set_option maxRecDepth 8192
set_option maxHeartbeats 2000000

namespace SunBeta
open scoped BigOperators
open Cert

theorem sumP_nonneg (n d : ℕ) (hn : 1≤n) (hd : d≤2*n) :
    0 ≤ ∑ p ∈ Finset.antidiagonal d, w n p.1*w n p.2*P n p.1 p.2 := by
  obtain ⟨D,c0,c1,hD,hcert⟩ := exists_certificate n d hd
  have ht := weighted_telescopes n d hn c0 c1
  have hpos : 0 ≤ ∑ p ∈ Finset.antidiagonal d, w n p.1*w n p.2*Q n p.1 p.2 D c0 c1 := by
    apply Finset.sum_nonneg
    intro p hp
    have hkl := Finset.mem_antidiagonal.mp hp
    by_cases hk : p.1≤n+1
    · by_cases hl : p.2≤n+1
      · exact mul_nonneg (mul_nonneg (w_nonneg _ _) (w_nonneg _ _)) (hcert _ _ hkl hk hl)
      · rw [w_zero (by omega : n+1<p.2)]
        simp
    · rw [w_zero (by omega : n+1<p.1)]
      simp
  have heq : (∑ p ∈ Finset.antidiagonal d, w n p.1*w n p.2*Q n p.1 p.2 D c0 c1) =
      D*(∑ p ∈ Finset.antidiagonal d, w n p.1*w n p.2*P n p.1 p.2) := by
    calc
      (∑ p ∈ Finset.antidiagonal d, w n p.1*w n p.2*Q n p.1 p.2 D c0 c1) =
        ∑ p ∈ Finset.antidiagonal d, (D*(w n p.1*w n p.2*P n p.1 p.2)+
          w n p.1*w n p.2*(c0*T0 n p.1 p.2+c1*T1 n p.1 p.2)) := by
            apply Finset.sum_congr rfl
            intro p hp
            unfold Q
            ring
      _ = _ := by rw [Finset.sum_add_distrib, ← Finset.mul_sum, ht, add_zero]
  rw [heq] at hpos
  exact nonneg_of_mul_nonneg_right hpos hD

theorem delta_nonneg (s d : ℕ) : 0≤delta s d := by
  by_cases hd : d≤2*(s+1)
  · have h := sumP_nonneg (s+1) d (by omega) hd
    have he := delta_sum s d
    simp only [Nat.cast_add, Nat.cast_one] at h
    rw [← he] at h
    have hpos : (0:ℚ)<2*((s:ℚ)+1) := by positivity
    exact nonneg_of_mul_nonneg_right h hpos
  · unfold delta
    apply Finset.sum_nonneg
    intro p hp
    have hkl := Finset.mem_antidiagonal.mp hp
    have hleft : a s p.1*a (s+2) p.2=0 := by
      by_cases hk : s<p.1
      · rw [a_zero hk]; ring
      · have hl : s+2<p.2 := by omega
        rw [a_zero hl]; ring
    have hright : a (s+1) p.1*a (s+1) p.2=0 := by
      by_cases hk : s+1<p.1
      · rw [a_zero hk]; ring
      · have hl : s+1<p.2 := by omega
        rw [a_zero hl]; ring
    rw [hleft,hright]
    norm_num

theorem logconvex_step (s d : ℕ) :
    0≤(beta s*beta (s+2)-beta (s+1)^2).coeff d := by
  have h : (0:ℚ)≤((beta s*beta (s+2)-beta (s+1)^2).coeff d : ℤ) := by
    rw [delta_coeff]
    exact delta_nonneg s d
  exact_mod_cast h

/-- Sun's original beta-polynomial coefficientwise log-convexity statement.
    Every center n ≥ 1 and every degree d ≥ 0 are included. -/
theorem beta_coeffwise_logconvex (n : ℕ) (hn : 1≤n) (d : ℕ) :
    0≤(beta (n-1)*beta (n+1)-beta n^2).coeff d := by
  have h := logconvex_step (n-1) d
  have h1 : n-1+1=n := by omega
  have h2 : n-1+2=n+1 := by omega
  simpa only [h1,h2] using h

#print axioms SunBeta.beta_coeffwise_logconvex

end SunBeta
