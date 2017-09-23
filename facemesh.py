# Face Mesh
# Written by Or Fleisher for Data Art class taught in ITP, NYU during fall 2017 by Genevieve Hoffman.
# Based on Leon Eckerts code from the facemesh workshop - https://github.com/leoneckert/facemash-workshop

import cv2
import dlib
import sys, os, time, random
import numpy as np

class FaceMesh:
    def __init__(self, pred):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(pred)

    def get_img(self, path):
        print("[+] Opened image from:", path)
        return cv2.imread(path)

    def get_rects(self, img):
        rects = self.detector(img)
        print("[+] Number of faces found:", len(rects))
        return rects

    def get_landmarks(self, img, rect):
        return np.matrix([[p.x, p.y] for p in self.predictor(img, rect).parts()])

    # https://matthewearl.github.io/2015/07/28/switching-eds-with-python/
    def transformation_from_points(self, points1, points2):
        points1 = points1.astype(np.float64)
        points2 = points2.astype(np.float64)

        c1 = np.mean(points1, axis=0)
        c2 = np.mean(points2, axis=0)
        points1 -= c1
        points2 -= c2

        s1 = np.std(points1)
        s2 = np.std(points2)
        points1 /= s1
        points2 /= s2

        U, S, Vt = np.linalg.svd(points1.T * points2)
        R = (U * Vt).T

        return np.vstack([np.hstack(((s2 / s1) * R,
                                           c2.T - (s2 / s1) * R * c1.T)),
                             np.matrix([0., 0., 1.])])

    def warp_im(self, im, M, dshape):
        output_im = np.ones(dshape, dtype=im.dtype)*255
        translationMatrix = np.matrix([0, 0])
        moveImageSet = cv2.transform(dshape, translationMatrix)
        cv2.warpAffine(im,
                       M[:2],
                       (dshape[1], dshape[0]),
                       dst=output_im,
                       borderMode=cv2.BORDER_TRANSPARENT,
                       flags=cv2.WARP_INVERSE_MAP)

        return output_im

    def align(self, folderPath):
        imgs = []
        count = 0
        for img_file in os.listdir(folderPath):
            path = folderPath + "/" + img_file
            print(count, ":", path)
            if count == 0:
                # get our reference image
                ref_img = self.get_img(path)
                rects = self.get_rects(ref_img)
                if len(rects) > 0:
                    ref_rect = rects[0]
                else:
                    continue
                ref_landmarks = self.get_landmarks(ref_img, ref_rect)
                average = ref_img.copy()
                # cv2.namedWindow("average", cv2.WINDOW_NORMAL)
                # cv2.imshow('average', average)
                # cv2.waitKey(0)


            else:
                # do the thing
                img = self.get_img(path)
                rects = self.get_rects(img)
                if len(rects) > 0:
                    rect = rects[0]
                else:
                    continue

                landmarks = self.get_landmarks(img, rect)

                transformation_matrix = self.transformation_from_points(ref_landmarks, landmarks)
                warped_img = self.warp_im(img, transformation_matrix, ref_img.shape)

                # cv2.imshow('average', np.mean(alignedImgs, axis=0))
                imgs.append(warped_img)
                data = np.array(imgs)
                self.avrege = np.mean(data, axis = 0)
                cv2.imshow("average", self.avrege.astype('uint8'))
                cv2.waitKey(1)

            count += 1
        return imgs
        cv2.waitKey(0)

    def getAvarage(self):
        return self.avrege
