# -*- coding: utf-8 -*- 
#                                                     #
#  __authors__ = Adarsh Kalikadien & Vivek Sinha      #
#  __institution__ = TU Delft                         #
#                                                     #
"""A different approach to the same problem: The use case would be given a C-H bond to be functionalized:
generate 3 atoms A,B,C such that H,A,B,C make a tetrahedron
then H can be replaced/substituted by say another atoms Z (practical case would be C,N,P)
in the end this code will also allow substitution by O-CH3 type groups
"""
import numpy as np
import pandas as pd


class Complex:
    def __init__(self, path_to_data):
        self.path = path_to_data
        self.data_matrix = pd.read_table(self.path, skiprows=2, delim_whitespace=True,
                                         names=['atom', 'x', 'y', 'z'])  # read standard .xyz file
        self.atom_to_be_functionalized_index = 0
        self.atom_to_be_functionalized_xyz = self.data_matrix.loc[
            self.atom_to_be_functionalized_index, ['x', 'y', 'z']]  # get xyz coordinate of atom to be functionalized
        self.bonded_atom_index = 1
        self.bonded_atom_xyz = self.data_matrix.loc[
            self.bonded_atom_index, ['x', 'y', 'z']]  # get xyz coordinate of bonded atom
        self.bond_length = self.atom_to_be_functionalized_xyz - self.bonded_atom_xyz  # bond between current C-H
        self.bond_length_norm = self.bond_length / np.linalg.norm(self.bond_length)  # real bond length between C-H
        self.equilateral_triangle = np.array([[0, 1/np.sqrt(3.0), 0],
                                              [-0.5, -0.5/np.sqrt(3.0), 0],
                                              [0.5, -0.5/np.sqrt(3.0), 0]])

    @staticmethod
    def distance(a, b):
        d = a - b
        return np.sqrt(d[0] * d[0] + d[1] * d[1] + d[2] * d[2])

    @staticmethod
    def find_angle(v1, v2):
        cos_th = (v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        return np.arccos(cos_th) * 57.3

    def find_centroid(self):
        b = self.distance(self.atom_to_be_functionalized_xyz, self.bonded_atom_xyz)  # bond to be functionalized
        b = b * (2.0 * np.sqrt(2.0 / 3.0))
        self.equilateral_triangle = b*self.equilateral_triangle
        centroid = self.atom_to_be_functionalized_xyz + (b/3.0) * self.bond_length_norm
        return centroid

    def generate_substituent_vectors(self):
        centroid = self.find_centroid()
        v1 = self.equilateral_triangle[0, :]
        v2 = self.equilateral_triangle[1, :]
        v3 = self.equilateral_triangle[2, :]
        normal_vector = np.array([0, 0, 1])
        normal_vector = normal_vector / np.linalg.norm(normal_vector)  # real length of vector
        starting_coordinate = np.zeros(3)
        # theta = np.arccos(np.dot(self.bond_length_norm.T, normal_vector.T))

        bond_length_norm = np.array(self.bond_length_norm.astype('float64'))
        v = np.cross(normal_vector.T, bond_length_norm.T)
        v_x = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
        v_xsq = np.dot(v_x, v_x)
        c = np.dot(np.array(self.bond_length_norm).T, normal_vector.T)
        rotation_matrix = np.eye(3) + v_x + v_xsq * (1 / (1 + c))

        substituent_1_vector = np.dot(rotation_matrix, v1)
        substituent_2_vector = np.dot(rotation_matrix, v2.T)
        substituent_3_vector = np.dot(rotation_matrix, v3.T)

        substituent_1_vector = -(starting_coordinate - centroid) + substituent_1_vector
        substituent_2_vector = -(starting_coordinate - centroid) + substituent_2_vector
        substituent_3_vector = -(starting_coordinate - centroid) + substituent_3_vector

        return substituent_1_vector, substituent_2_vector, substituent_3_vector

    def write_xyz(self, filename, substituent_1_atom, substituent_2_atom, substituent_3_atom):
        v_1, v_2, v_3 = self.generate_substituent_vectors()

        atom_to_be_functionalized = self.data_matrix.loc[
            self.atom_to_be_functionalized_index, ['atom', 'x', 'y', 'z']]
        atom_to_be_functionalized = pd.DataFrame([[atom_to_be_functionalized[0], atom_to_be_functionalized[1],
                                                   atom_to_be_functionalized[2], atom_to_be_functionalized[3]]], columns=['atom', 'x', 'y', 'z']).set_index('atom')
        bonded_atom = self.data_matrix.loc[
            self.bonded_atom_index, ['atom', 'x', 'y', 'z']]
        bonded_atom = pd.DataFrame([[bonded_atom[0], bonded_atom[1], bonded_atom[2], bonded_atom[3]]],
                                   columns=['atom', 'x', 'y', 'z']).set_index('atom')

        substituent_1 = pd.DataFrame([[substituent_1_atom, v_1[0], v_1[1], v_1[2]]], columns=['atom', 'x', 'y', 'z']).set_index('atom')
        substituent_2 = pd.DataFrame([[substituent_2_atom, v_2[0], v_2[1], v_2[2]]], columns=['atom', 'x', 'y', 'z']).set_index('atom')
        substituent_3 = pd.DataFrame([[substituent_3_atom, v_3[0], v_3[1], v_3[2]]], columns=['atom', 'x', 'y', 'z']).set_index('atom')

        write_data = pd.concat([atom_to_be_functionalized, bonded_atom, substituent_1, substituent_2, substituent_3])

        # write correct .xyz format
        with open(filename, 'a') as file:
            file.write('4\n')
            file.write('\n')
        file.close()
        write_data.to_csv(filename, sep=' ', header=False, mode='a')

        # remove last whiteline generated by pandas' to_csv function
        with open(filename) as f:
            lines = f.readlines()
            last = len(lines) - 1
            lines[last] = lines[last].replace('\r', '').replace('\n', '')
        with open(filename, 'w') as wr:
            wr.writelines(lines)


if __name__ == '__main__':
    methyl = Complex('substituents_xyz/CH3.xyz')

    # print(methyl.atom_to_be_functionalized_xyz)
    # print(methyl.bonded_atom_xyz)
    # methyl.generate_substituent_vectors()

    methyl.write_xyz('test.xyz', 'H', 'H', 'H')

    # v_1, v_2, v_3 = methyl.generate_substituent_vectors()
    # print("H", methyl.bonded_atom_xyz[0], methyl.bonded_atom_xyz[1], methyl.bonded_atom_xyz[2])
    # print("C", methyl.atom_to_be_functionalized_xyz[0], methyl.atom_to_be_functionalized_xyz[1], methyl.atom_to_be_functionalized_xyz[2])
    # print("H", v_1[0], v_1[1], v_1[2])
    # print("H", v_2[0], v_2[1], v_2[2])
    # print("H", v_3[0], v_3[1], v_3[2])
