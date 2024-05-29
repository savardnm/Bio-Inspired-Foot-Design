
finger_normal = [196.25,192.55,196.25,186.00,186.75,184.80,192.55,189.45,186.00,186.75,193.40,193.40,189.45,192.55,192.55,193.40,184.80,192.55,193.40,186.00];
louse_normal = [193.10,220.70,704.65,531.20,263.10,381.35,259.40,268.30,652.10,239.50,408.15,1449.75,371.05,236.45,374.00,285.35,328.40,556.70];

finger_shear = [208.25,219.60,219.70,242.50,226.65,219.60,216.50,224.75,219.15,222.50,224.75,241.20,189.65,181.85,189.65,181.85,219.60,219.70,224.75,189.65];
louse_shear = [120.94,214.00,136.55,211.60,189.45,228.10,101.10,164.80,238.15,112.75,135.55,101.10,161.10,101.10];

revolute_normal_trimmed = [290.14,289.55,289.80,289.55,289.80,288.45,]
prismatic_normal_trimmed = [101.15,101.15,101.15,101.15,101.15,101.15,]

revolute_shear_trimmed = [165.85,165.70,165.60,165.60,170.00,165.70,]
prismatic_shear_trimmed = [55.30,52.65,52.65,55.30,55.30,52.65,]

finger_normal_trimmed = [196.25,192.55,196.25,186.00,186.75,184.80,192.55,189.45,186.00,186.75,193.40,193.40, 189.45,192.55];
louse_normal_trimmed =  [193.10,220.70,704.65,531.20,263.10,381.35,259.40,268.30,652.10,239.50,408.15,1449.75,371.05,236.45];

finger_shear_trimmed =  [208.25,219.60,219.70,242.50,226.65,219.60,216.50,224.75,219.15,222.50,224.75,241.20, 189.65,181.85];
louse_shear_trimmed =   [120.94,214.00,136.55,211.60,189.45,228.10,101.10,164.80,238.15,112.75,135.55,101.10, 161.10,101.10];

finger_overall = finger_normal_trimmed .* finger_shear_trimmed
louse_overall  = louse_normal_trimmed .* louse_shear_trimmed

prismatic_overall = prismatic_normal_trimmed .* prismatic_shear_trimmed
revolute_overall = revolute_normal_trimmed .* revolute_shear_trimmed

[overall_h,p] = ttest2(finger_overall,louse_overall,"Tail","left", 'Vartype','unequal')
[overall_h,p] = ttest2(louse_overall,finger_overall,"Tail","left", 'Vartype','unequal')

% % 
% [normal_h,p] = ttest2(finger_normal,louse_normal,"Tail","left", 'Vartype','unequal')

% [shear_h,p] = ttest2(finger_shear,louse_shear, "Tail","left", 'Vartype','unequal')


% [normal_h,p] = ttest2(louse_normal,finger_normal,"Tail","left", 'Vartype','unequal')

% [shear_h,p] = ttest2(louse_shear,finger_shear, "Tail","left", 'Vartype','unequal')

% Are they from DIFFERENT POPULATIONS???
% [normal_h,p] = ttest2(finger_normal,louse_normal, 'Vartype','unequal')

% [shear_h,p] = ttest2(finger_shear,louse_shear, 'Vartype','unequal')
% h=1, so yes, ,they are clearly different populations